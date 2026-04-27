from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import requirement_service
from backend.services.uml import usecase_service
from backend.services.uml import class_digram_service
from backend.services.uml import activity_digram_service
from backend.services.uml import sequence_digram_service
from backend.services.uml.persistence import get_cached_diagram, get_all_sequence_diagrams, get_latest_sequence_by_usecase_idx
from backend.models.project import Project
from io import BytesIO
import tempfile
import os
import requests
from typing import Dict, Any

router = APIRouter()

# We'll use reportlab for PDF generation as it's more reliable for complex layouts
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will not work.")

# Default model settings
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.4-mini"

async def _ensure_diagram_exists(db: Session, project_id: int, diagram_type: str, usecase_idx: int = None):
    """Ensure diagram exists, generate if missing."""
    print(f"Checking if {diagram_type} diagram exists for project {project_id}")
    
    if diagram_type == 'usecase':
        cached = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if not cached:
            print(f"Use case diagram missing, generating...")
            formatted = _get_formatted_requirements(project_id, db)
            await usecase_service.generate_usecase(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    
    elif diagram_type == 'class':
        cached = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if not cached:
            print(f"Class diagram missing, generating...")
            formatted = _get_formatted_requirements(project_id, db)
            await class_digram_service.generate_class(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    
    elif diagram_type == 'activity':
        cached = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
        if not cached:
            print(f"Activity diagram missing, generating...")
            formatted = _get_formatted_requirements(project_id, db)
            await activity_digram_service.generate_activity(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    
    elif diagram_type == 'sequence' and usecase_idx is not None:
        cached = get_latest_sequence_by_usecase_idx(db, project_id, usecase_idx)
        if not cached:
            print(f"Sequence diagram {usecase_idx} missing, generating...")
            formatted = _get_formatted_requirements(project_id, db)
            await sequence_digram_service.generate_sequence(db, project_id, usecase_idx, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)


def _get_formatted_requirements(project_id: int, db: Session) -> str:
    """Helper to get formatted requirements for diagram generation."""
    requirements = requirement_service.get_project_requirements(db, project_id, False)
    formatted_lines = ["### Project Functional Requirements List:"]
    counter = 1
    for req in requirements:
        if req.is_active and req.type == 'Functional':
            line = f"{counter}. {req.description} [Priority: {req.priority.name}]"
            formatted_lines.append(line)
            counter += 1
    if counter == 1:
        return ""
    return "\n".join(formatted_lines)


def _get_requirements_content(project_id: int, db: Session) -> Dict[str, Any]:
    """Fetch and format requirements for PDF."""
    print(f"Fetching requirements for project {project_id}")
    requirements = requirement_service.get_project_requirements(db, project_id, False)
    print(f"Found {len(requirements)} total requirements")
    
    functional = [req for req in requirements if req.type == 'Functional' and req.is_active]
    non_functional = [req for req in requirements if req.type == 'Non-Functional' and req.is_active]
    
    print(f"Found {len(functional)} functional and {len(non_functional)} non-functional requirements")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        'functional': functional,
        'non_functional': non_functional,
        'project_name': project.app_name
    }


def _download_svg_as_temp_file(svg_url: str) -> str:
    """Download SVG and convert to temporary PNG file for PDF inclusion."""
    try:
        print(f"Downloading SVG from: {svg_url}")
        # Download SVG
        response = requests.get(svg_url, timeout=30)
        response.raise_for_status()
        
        if not response.content:
            print("Empty SVG content received")
            return None
            
        print(f"Downloaded {len(response.content)} bytes of SVG content")
        
        # Convert SVG to ReportLab drawing
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        
        drawing = svg2rlg(BytesIO(response.content))
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        
        # Render as PNG with higher DPI for better quality
        renderPM.drawToFile(drawing, temp_file.name, fmt='PNG', dpi=150)
        
        print(f"Successfully converted SVG to PNG: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"Error converting SVG from {svg_url}: {e}")
        import traceback
        traceback.print_exc()
        return None


def _create_pdf_content(content_data: Dict[str, Any], project_id: int, db: Session) -> BytesIO:
    """Create PDF content with all diagrams and requirements."""
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF generation not available - reportlab not installed")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue,
        spaceBefore=20
    )
    
    story = []
    
    # Title
    project_name = content_data['project_name']
    story.append(Paragraph(f"Comprehensive SRS Report<br/>{project_name}", title_style))
    story.append(Spacer(1, 20))
    
    # 1. Functional Requirements
    if content_data['functional']:
        story.append(Paragraph("1. Functional Requirements", heading_style))
        for i, req in enumerate(content_data['functional'], 1):
            # Handle both ORM objects and dictionaries
            req_title = getattr(req, 'title', None) or getattr(req, 'description', None) or f'Functional Requirement {i}'
            req_desc = getattr(req, 'description', None) or 'No description available'
            story.append(Paragraph(f"<b>{i}. {req_title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req_desc}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))
    
    # 2. Non-Functional Requirements
    if content_data['non_functional']:
        story.append(Paragraph("2. Non-Functional Requirements", heading_style))
        for i, req in enumerate(content_data['non_functional'], 1):
            # Handle both ORM objects and dictionaries
            req_title = getattr(req, 'title', None) or getattr(req, 'description', None) or f'Non-Functional Requirement {i}'
            req_desc = getattr(req, 'description', None) or 'No description available'
            story.append(Paragraph(f"<b>{i}. {req_title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req_desc}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))
    
    # Helper function to add diagram
    def add_diagram(title: str, svg_url: str, diagram_type: str):
        """Add a diagram to the PDF."""
        try:
            story.append(Paragraph(title, heading_style))
            
            # Convert SVG to temporary PNG
            temp_file = _download_svg_as_temp_file(svg_url)
            if temp_file:
                # Add image to PDF
                img = Image(temp_file, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 20))
                
                # Clean up temp file
                os.unlink(temp_file)
            else:
                story.append(Paragraph(f"[{diagram_type} diagram could not be rendered]", styles['Normal']))
                story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error adding {diagram_type} diagram: {e}")
            story.append(Paragraph(f"[Error loading {diagram_type} diagram]", styles['Normal']))
            story.append(Spacer(1, 20))
    
    # 3. Class Diagram
    try:
        print("Looking for Class diagram...")
        class_diagram = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        print(f"Class diagram found: {class_diagram is not None}")
        if class_diagram and class_diagram.get('svg_url'):
            print(f"Adding Class diagram with URL: {class_diagram['svg_url']}")
            add_diagram("3. Class Diagram", class_diagram['svg_url'], "Class")
        else:
            print("No Class diagram found or no SVG URL")
    except Exception as e:
        print(f"Error getting class diagram: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Use Case Diagram
    try:
        print("Looking for Use Case diagram...")
        usecase_diagram = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        print(f"Use Case diagram found: {usecase_diagram is not None}")
        if usecase_diagram and usecase_diagram.get('svg_url'):
            print(f"Adding Use Case diagram with URL: {usecase_diagram['svg_url']}")
            add_diagram("4. Use Case Diagram", usecase_diagram['svg_url'], "Use Case")
        else:
            print("No Use Case diagram found or no SVG URL")
    except Exception as e:
        print(f"Error getting use case diagram: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Sequence Diagrams (Loop through all use cases)
    try:
        print("Looking for Sequence diagrams...")
        sequence_diagrams = get_all_sequence_diagrams(db, project_id)
        print(f"Found {len(sequence_diagrams) if sequence_diagrams else 0} sequence diagrams")
        if sequence_diagrams:
            story.append(Paragraph("5. Sequence Diagrams", heading_style))
            for i, seq_diagram in enumerate(sequence_diagrams, 1):
                print(f"Processing sequence diagram {i}: usecase_idx={getattr(seq_diagram, 'usecase_idx', 'unknown')}")
                svg_url = getattr(seq_diagram, 'svg_url', None)
                if svg_url:
                    story.append(Paragraph(f"5.{i} Sequence Diagram for Use Case {seq_diagram.usecase_idx}", styles['Heading3']))
                    temp_file = _download_svg_as_temp_file(svg_url)
                    if temp_file:
                        img = Image(temp_file, width=6*inch, height=4*inch)
                        img.hAlign = 'CENTER'
                        story.append(img)
                        story.append(Spacer(1, 15))
                        os.unlink(temp_file)
                    else:
                        story.append(Paragraph(f"[Sequence diagram {seq_diagram.usecase_idx} could not be rendered]", styles['Normal']))
                        story.append(Spacer(1, 15))
                else:
                    print(f"No SVG URL for sequence diagram {i}")
            story.append(Spacer(1, 20))
        else:
            print("No sequence diagrams found")
    except Exception as e:
        print(f"Error getting sequence diagrams: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Activity Diagram
    try:
        print("Looking for Activity diagram...")
        activity_diagram = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
        print(f"Activity diagram found: {activity_diagram is not None}")
        if activity_diagram and activity_diagram.get('svg_url'):
            print(f"Adding Activity diagram with URL: {activity_diagram['svg_url']}")
            add_diagram("6. Activity Diagram", activity_diagram['svg_url'], "Activity")
        else:
            print("No Activity diagram found or no SVG URL")
    except Exception as e:
        print(f"Error getting activity diagram: {e}")
        import traceback
        traceback.print_exc()
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


async def pdf_master_orchestrator(
    project_id: int, 
    db: Session,
    force_regenerate: bool = False
) -> Dict[str, Any]:
    """
    PDF Master Orchestrator - Sequentially generates and validates all components before PDF creation.
    
    Logic Flow:
    1. Verify Functional and Non-Functional Requirements exist
    2. Generate/verify Class Diagram
    3. Generate/verify Use Case Diagram  
    4. Generate/verify all individual Sequence Diagrams (looping through every Use Case)
    5. Generate/verify Activity Diagram
    6. Compile comprehensive PDF with consistent styling
    
    Args:
        project_id: Project identifier
        db: Database session
        force_regenerate: Force regeneration of all components
        
    Returns:
        Dictionary with PDF generation results and component status
    """
    print(f"🚀 PDF Master Orchestrator started for project {project_id}")
    
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500, 
            detail="PDF generation not available. Please install reportlab: pip install reportlab"
        )
    
    # Track component generation status
    component_status = {
        "requirements": False,
        "class_diagram": False,
        "usecase_diagram": False,
        "sequence_diagrams": [],
        "activity_diagram": False
    }
    
    try:
        # Step 1: Verify Requirements exist
        print("📋 Step 1: Verifying requirements...")
        content_data = _get_requirements_content(project_id, db)
        if content_data['functional'] or content_data['non_functional']:
            component_status["requirements"] = True
            print(f"✅ Requirements verified: {len(content_data['functional'])} functional, {len(content_data['non_functional'])} non-functional")
        else:
            raise ValueError("No requirements found for this project")
        
        # Step 2: Generate/verify Class Diagram
        print("🏗️ Step 2: Generating/verifying Class Diagram...")
        if force_regenerate:
            # Force regeneration by clearing cache
            formatted = _get_formatted_requirements(project_id, db)
            await class_digram_service.generate_class(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
        
        await _ensure_diagram_exists(db, project_id, 'class')
        class_diagram = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if class_diagram and class_diagram.get('svg_url'):
            component_status["class_diagram"] = True
            print("✅ Class Diagram verified")
        else:
            raise ValueError("Failed to generate Class Diagram")
        
        # Step 3: Generate/verify Use Case Diagram
        print("🎭 Step 3: Generating/verifying Use Case Diagram...")
        if force_regenerate:
            formatted = _get_formatted_requirements(project_id, db)
            await usecase_service.generate_usecase(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
        
        await _ensure_diagram_exists(db, project_id, 'usecase')
        usecase_diagram = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if usecase_diagram and usecase_diagram.get('svg_url'):
            component_status["usecase_diagram"] = True
            use_cases = usecase_diagram.get('data', {}).get('use_cases', [])
            print(f"✅ Use Case Diagram verified with {len(use_cases)} use cases")
        else:
            raise ValueError("Failed to generate Use Case Diagram")
        
        # Step 4: Generate/verify all Sequence Diagrams
        print("🔄 Step 4: Generating/verifying all Sequence Diagrams...")
        if use_cases:
            for i, use_case in enumerate(use_cases):
                print(f"   Processing sequence diagram {i+1}/{len(use_cases)}: {use_case}")
                try:
                    if force_regenerate:
                        formatted = _get_formatted_requirements(project_id, db)
                        await sequence_digram_service.generate_sequence(db, project_id, i, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
                    
                    await _ensure_diagram_exists(db, project_id, 'sequence', i)
                    seq_diagram = get_latest_sequence_by_usecase_idx(db, project_id, i)
                    
                    if seq_diagram and seq_diagram.get('svg_url'):
                        component_status["sequence_diagrams"].append({
                            "usecase_idx": i,
                            "usecase_name": use_case,
                            "status": True,
                            "svg_url": seq_diagram['svg_url']
                        })
                        print(f"   ✅ Sequence diagram {i} verified")
                    else:
                        print(f"   ❌ Failed to generate sequence diagram {i}")
                        component_status["sequence_diagrams"].append({
                            "usecase_idx": i,
                            "usecase_name": use_case,
                            "status": False
                        })
                except Exception as seq_err:
                    print(f"   ❌ Error generating sequence diagram {i}: {seq_err}")
                    component_status["sequence_diagrams"].append({
                        "usecase_idx": i,
                        "usecase_name": use_case,
                        "status": False,
                        "error": str(seq_err)
                    })
        
        # Step 5: Generate/verify Activity Diagram
        print("⚡ Step 5: Generating/verifying Activity Diagram...")
        try:
            if force_regenerate:
                formatted = _get_formatted_requirements(project_id, db)
                await activity_digram_service.generate_activity(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
            
            await _ensure_diagram_exists(db, project_id, 'activity')
            activity_diagram = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
            if activity_diagram and activity_diagram.get('svg_url'):
                component_status["activity_diagram"] = True
                print("✅ Activity Diagram verified")
            else:
                print("❌ Failed to generate Activity Diagram, continuing without it")
                component_status["activity_diagram"] = False
        except Exception as act_err:
            print(f"❌ Error generating Activity Diagram: {act_err}")
            component_status["activity_diagram"] = False
        
        # Step 6: Compile comprehensive PDF
        print("📄 Step 6: Compiling comprehensive PDF...")
        pdf_buffer = _create_pdf_content(content_data, project_id, db)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(pdf_buffer.getvalue())
        temp_file.close()
        
        print(f"✅ PDF Master Orchestrator completed successfully!")
        print(f"📊 Component Status: {component_status}")
        
        return {
            "success": True,
            "message": "PDF generated successfully",
            "pdf_url": f"/api/temp-files/{os.path.basename(temp_file.name)}",
            "filename": f"{content_data['project_name']}_Comprehensive_Report.pdf",
            "component_status": component_status,
            "stats": {
                "functional_requirements": len(content_data['functional']),
                "non_functional_requirements": len(content_data['non_functional']),
                "sequence_diagrams": len([s for s in component_status["sequence_diagrams"] if s["status"]])
            }
        }
        
    except Exception as e:
        print(f"❌ PDF Master Orchestrator failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "component_status": component_status,
            "message": "PDF generation failed"
        }


@router.get("/generate-pdf/{project_id}")
async def generate_pdf(
    project_id: int,
    db: Session = Depends(get_db),
    force: bool = Query(False, description="Force regeneration of all components"),
):
    """Generate comprehensive PDF report with SRS and all UML diagrams using the PDF Master Orchestrator."""
    
    try:
        result = await pdf_master_orchestrator(project_id, db, force_regenerate=force)
        
        if result["success"]:
            return {
                "message": result["message"],
                "pdf_url": result["pdf_url"],
                "filename": result["filename"],
                "stats": result["stats"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        print(f"Error in PDF generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
