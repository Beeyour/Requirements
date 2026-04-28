from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
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

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.4-mini"

async def _ensure_diagram_exists(db: Session, project_id: int, diagram_type: str, usecase_idx: int = None):
    # auto-generates a diagram on-the-fly if it's missing from the DB
    if diagram_type == 'usecase':
        cached = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if not cached:
            formatted = _get_formatted_requirements(project_id, db)
            await usecase_service.generate_usecase(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

    elif diagram_type == 'class':
        cached = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if not cached:
            formatted = _get_formatted_requirements(project_id, db)
            await class_digram_service.generate_class(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

    elif diagram_type == 'activity':
        cached = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
        if not cached:
            formatted = _get_formatted_requirements(project_id, db)
            await activity_digram_service.generate_activity(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

    elif diagram_type == 'sequence' and usecase_idx is not None:
        cached = get_latest_sequence_by_usecase_idx(db, project_id, usecase_idx)
        if not cached:
            formatted = _get_formatted_requirements(project_id, db)
            await sequence_digram_service.generate_sequence(db, project_id, usecase_idx, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)


def _get_formatted_requirements(project_id: int, db: Session) -> str:
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
    requirements = requirement_service.get_project_requirements(db, project_id, False)
    functional = [req for req in requirements if req.type == 'Functional' and req.is_active]
    non_functional = [req for req in requirements if req.type == 'Non-Functional' and req.is_active]

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        'functional': functional,
        'non_functional': non_functional,
        'project_name': project.app_name
    }


def _download_svg_as_temp_file(svg_url: str) -> str:
    # SVG → PNG pipeline: download, parse via svglib, render via reportlab
    # Returns path to a temp PNG file (caller must clean up), or None on failure
    try:
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
        except ImportError as imp_err:
            print(f"SVG conversion skipped — missing dependency: {imp_err}")
            return None

        response = requests.get(svg_url, timeout=30)
        response.raise_for_status()

        if not response.content:
            return None

        drawing = svg2rlg(BytesIO(response.content))

        if drawing is None:
            return None

        if drawing.width <= 0 or drawing.height <= 0:
            return None

        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        renderPM.drawToFile(drawing, temp_file.name, fmt='PNG', dpi=150)

        return temp_file.name
    except Exception as e:
        print(f"Error converting SVG from {svg_url}: {e}")
        import traceback
        traceback.print_exc()
        return None


def _create_pdf_content(content_data: Dict[str, Any], project_id: int, db: Session) -> BytesIO:
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=500, detail="PDF generation not available - reportlab not installed")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=1
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
    temp_files_to_cleanup = []

    project_name = content_data['project_name']
    story.append(Paragraph(f"Comprehensive SRS Report<br/>{project_name}", title_style))
    story.append(Spacer(1, 20))

    if content_data['functional']:
        story.append(Paragraph("1. Functional Requirements", heading_style))
        for i, req in enumerate(content_data['functional'], 1):
            req_title = getattr(req, 'title', None) or getattr(req, 'description', None) or f'Functional Requirement {i}'
            req_desc = getattr(req, 'description', None) or 'No description available'
            story.append(Paragraph(f"<b>{i}. {req_title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req_desc}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))

    if content_data['non_functional']:
        story.append(Paragraph("2. Non-Functional Requirements", heading_style))
        for i, req in enumerate(content_data['non_functional'], 1):
            req_title = getattr(req, 'title', None) or getattr(req, 'description', None) or f'Non-Functional Requirement {i}'
            req_desc = getattr(req, 'description', None) or 'No description available'
            story.append(Paragraph(f"<b>{i}. {req_title}</b>", styles['Normal']))
            story.append(Paragraph(f"{req_desc}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 20))

    def add_diagram(title: str, svg_url: str, diagram_type: str):
        try:
            story.append(Paragraph(title, heading_style))
            temp_file = _download_svg_as_temp_file(svg_url)
            if temp_file:
                img = Image(temp_file, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 20))
                # must keep temp file alive until doc.build() reads it
                temp_files_to_cleanup.append(temp_file)
            else:
                story.append(Paragraph(f"[{diagram_type} diagram could not be rendered]", styles['Normal']))
                story.append(Spacer(1, 20))
        except Exception as e:
            print(f"Error adding {diagram_type} diagram: {e}")
            story.append(Paragraph(f"[Error loading {diagram_type} diagram]", styles['Normal']))
            story.append(Spacer(1, 20))

    try:
        class_diagram = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if class_diagram and class_diagram.get('svg_url'):
            add_diagram("3. Class Diagram", class_diagram['svg_url'], "Class")
    except Exception as e:
        print(f"Error getting class diagram: {e}")
        import traceback
        traceback.print_exc()

    try:
        usecase_diagram = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if usecase_diagram and usecase_diagram.get('svg_url'):
            add_diagram("4. Use Case Diagram", usecase_diagram['svg_url'], "Use Case")
    except Exception as e:
        print(f"Error getting use case diagram: {e}")
        import traceback
        traceback.print_exc()

    try:
        sequence_diagrams = get_all_sequence_diagrams(db, project_id)
        if sequence_diagrams:
            story.append(Paragraph("5. Sequence Diagrams", heading_style))
            for i, seq_diagram in enumerate(sequence_diagrams, 1):
                svg_url = getattr(seq_diagram, 'svg_url', None)
                if svg_url:
                    story.append(Paragraph(f"5.{i} Sequence Diagram for Use Case {seq_diagram.usecase_idx}", styles['Heading3']))
                    temp_file = _download_svg_as_temp_file(svg_url)
                    if temp_file:
                        img = Image(temp_file, width=6*inch, height=4*inch)
                        img.hAlign = 'CENTER'
                        story.append(img)
                        story.append(Spacer(1, 15))
                        temp_files_to_cleanup.append(temp_file)
                    else:
                        story.append(Paragraph(f"[Sequence diagram {seq_diagram.usecase_idx} could not be rendered]", styles['Normal']))
                        story.append(Spacer(1, 15))
            story.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error getting sequence diagrams: {e}")
        import traceback
        traceback.print_exc()

    try:
        activity_diagram = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
        if activity_diagram and activity_diagram.get('svg_url'):
            add_diagram("6. Activity Diagram", activity_diagram['svg_url'], "Activity")
    except Exception as e:
        print(f"Error getting activity diagram: {e}")
        import traceback
        traceback.print_exc()

    doc.build(story)

    # temp PNGs are only safe to delete after build() has consumed them
    for tf in temp_files_to_cleanup:
        try:
            os.unlink(tf)
        except OSError:
            pass

    buffer.seek(0)
    return buffer


async def pdf_master_orchestrator(
    project_id: int,
    db: Session,
    force_regenerate: bool = False
) -> Dict[str, Any]:
    # orchestrator: verifies/generates every artifact in order, then compiles the PDF
    # the order matters — e.g. sequence diagrams depend on use case data
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="PDF generation not available. Please install reportlab: pip install reportlab"
        )

    component_status = {
        "requirements": False,
        "class_diagram": False,
        "usecase_diagram": False,
        "sequence_diagrams": [],
        "activity_diagram": False
    }

    try:
        content_data = _get_requirements_content(project_id, db)
        if content_data['functional'] or content_data['non_functional']:
            component_status["requirements"] = True
        else:
            raise ValueError("No requirements found for this project")

        if force_regenerate:
            formatted = _get_formatted_requirements(project_id, db)
            await class_digram_service.generate_class(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

        await _ensure_diagram_exists(db, project_id, 'class')
        class_diagram = get_cached_diagram(db, class_digram_service.ClassDiagram, project_id)
        if class_diagram and class_diagram.get('svg_url'):
            component_status["class_diagram"] = True
        else:
            raise ValueError("Failed to generate Class Diagram")

        if force_regenerate:
            formatted = _get_formatted_requirements(project_id, db)
            await usecase_service.generate_usecase(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

        await _ensure_diagram_exists(db, project_id, 'usecase')
        usecase_diagram = get_cached_diagram(db, usecase_service.UseCaseDiagram, project_id)
        if usecase_diagram and usecase_diagram.get('svg_url'):
            component_status["usecase_diagram"] = True
            use_cases = usecase_diagram.get('data', {}).get('use_cases', [])
        else:
            raise ValueError("Failed to generate Use Case Diagram")

        # generate a sequence diagram per use case — failures are non-fatal
        if use_cases:
            for i, use_case in enumerate(use_cases):
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
                    else:
                        component_status["sequence_diagrams"].append({
                            "usecase_idx": i,
                            "usecase_name": use_case,
                            "status": False
                        })
                except Exception as seq_err:
                    component_status["sequence_diagrams"].append({
                        "usecase_idx": i,
                        "usecase_name": use_case,
                        "status": False,
                        "error": str(seq_err)
                    })

        # activity diagram is also non-fatal
        try:
            if force_regenerate:
                formatted = _get_formatted_requirements(project_id, db)
                await activity_digram_service.generate_activity(db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

            await _ensure_diagram_exists(db, project_id, 'activity')
            activity_diagram = get_cached_diagram(db, activity_digram_service.ActivityDiagram, project_id)
            if activity_diagram and activity_diagram.get('svg_url'):
                component_status["activity_diagram"] = True
            else:
                component_status["activity_diagram"] = False
        except Exception as act_err:
            component_status["activity_diagram"] = False

        pdf_buffer = _create_pdf_content(content_data, project_id, db)

        return {
            "success": True,
            "message": "PDF generated successfully",
            "pdf_buffer": pdf_buffer,
            "filename": f"{content_data['project_name']}_Comprehensive_Report.pdf",
            "component_status": component_status,
            "stats": {
                "functional_requirements": len(content_data['functional']),
                "non_functional_requirements": len(content_data['non_functional']),
                "sequence_diagrams": len([s for s in component_status["sequence_diagrams"] if s["status"]])
            }
        }

    except Exception as e:
        print(f"PDF Master Orchestrator failed: {e}")
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
    try:
        result = await pdf_master_orchestrator(project_id, db, force_regenerate=force)

        if result["success"]:
            pdf_buffer = result["pdf_buffer"]
            pdf_buffer.seek(0)
            filename = result["filename"]
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in PDF generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
