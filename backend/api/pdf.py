from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import requirement_service
from backend.services.uml import usecase_service
from backend.services.uml import class_digram_service
from backend.services.uml import activity_digram_service
from backend.services.uml import sequence_digram_service
from backend.services.uml.persistence import get_cached_diagram, get_all_sequence_diagrams
from backend.models.project import Project
from io import BytesIO
import tempfile
import os
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


def _get_requirements_content(project_id: int, db: Session) -> Dict[str, Any]:
    """Fetch and format requirements for PDF."""
    requirements = requirement_service.get_project_requirements(db, project_id, False)
    
    functional = [req for req in requirements if req.type == 'functional' and req.is_active]
    non_functional = [req for req in requirements if req.type == 'non_functional' and req.is_active]
    
    return {
        'functional': functional,
        'non_functional': non_functional,
        'project_name': db.query(Project).filter(Project.id == project_id).first().app_name
    }


def _download_svg_as_temp_file(svg_url: str) -> str:
    """Download SVG and convert to temporary PNG file for PDF inclusion."""
    import requests
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    
    try:
        # Download SVG
        response = requests.get(svg_url)
        response.raise_for_status()
        
        # Convert SVG to ReportLab drawing
        drawing = svg2rlg(BytesIO(response.content))
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        
        # Render as PNG
        renderPM.drawToFile(drawing, temp_file.name, fmt='PNG')
        
        return temp_file.name
    except Exception as e:
        print(f"Error converting SVG: {e}")
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
            story.append(Paragraph(f"<b>{i}. {req.title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req.description}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))
    
    # 2. Non-Functional Requirements
    if content_data['non_functional']:
        story.append(Paragraph("2. Non-Functional Requirements", heading_style))
        for i, req in enumerate(content_data['non_functional'], 1):
            story.append(Paragraph(f"<b>{i}. {req.title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req.description}", styles['Normal']))
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
        class_diagram = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if class_diagram and class_diagram.svg_url:
            add_diagram("3. Class Diagram", class_diagram.svg_url, "Class")
    except Exception as e:
        print(f"Error getting class diagram: {e}")
    
    # 4. Use Case Diagram
    try:
        usecase_diagram = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if usecase_diagram and usecase_diagram.svg_url:
            add_diagram("4. Use Case Diagram", usecase_diagram.svg_url, "Use Case")
    except Exception as e:
        print(f"Error getting use case diagram: {e}")
    
    # 5. Sequence Diagrams (Loop through all use cases)
    try:
        sequence_diagrams = get_all_sequence_diagrams(db, project_id)
        if sequence_diagrams:
            story.append(Paragraph("5. Sequence Diagrams", heading_style))
            for i, seq_diagram in enumerate(sequence_diagrams, 1):
                if seq_diagram.svg_url:
                    story.append(Paragraph(f"5.{i} Sequence Diagram for Use Case {seq_diagram.usecase_idx}", styles['Heading3']))
                    temp_file = _download_svg_as_temp_file(seq_diagram.svg_url)
                    if temp_file:
                        img = Image(temp_file, width=6*inch, height=4*inch)
                        img.hAlign = 'CENTER'
                        story.append(img)
                        story.append(Spacer(1, 15))
                        os.unlink(temp_file)
                    else:
                        story.append(Paragraph(f"[Sequence diagram {seq_diagram.usecase_idx} could not be rendered]", styles['Normal']))
                        story.append(Spacer(1, 15))
            story.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error getting sequence diagrams: {e}")
    
    # 6. Activity Diagram
    try:
        activity_diagram = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
        if activity_diagram and activity_diagram.svg_url:
            add_diagram("6. Activity Diagram", activity_diagram.svg_url, "Activity")
    except Exception as e:
        print(f"Error getting activity diagram: {e}")
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@router.get("/generate-pdf/{project_id}")
async def generate_pdf(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Generate comprehensive PDF report with SRS and all UML diagrams."""
    
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500, 
            detail="PDF generation not available. Please install reportlab: pip install reportlab"
        )
    
    try:
        # Get content data
        content_data = _get_requirements_content(project_id, db)
        
        # Generate PDF
        pdf_buffer = _create_pdf_content(content_data, project_id, db)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(pdf_buffer.getvalue())
        temp_file.close()
        
        # In a real application, you might want to upload this to a cloud storage
        # and return a permanent URL. For now, we'll return the temp file path.
        
        return {
            "message": "PDF generated successfully",
            "pdf_url": f"/api/temp-files/{os.path.basename(temp_file.name)}",
            "filename": f"{content_data['project_name']}_Comprehensive_Report.pdf"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/temp-files/{filename}")
async def get_temp_file(filename: str):
    """Serve temporary files (like generated PDFs)."""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=filename
    )
