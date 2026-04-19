from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Project, Requirement
from services.ai_agent import generate_uml_from_requirements
from typing import List

def get_project_or_404(db: Session, project_id: int, user_id: int):
    """Fetches a project or raises 404 if not found or unauthorized."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def process_uml_generation(db: Session, project: Project):
    """Gathers active requirements and generates UML code via AI Agent."""
    # 1. Fetch active requirements only
    requirements = (
        db.query(Requirement)
        .filter(Requirement.project_id == project.id, Requirement.is_active == True)
        .order_by(Requirement.type, Requirement.id)
        .all()
    )

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="No active requirements found for this project. Generate SRS first.",
        )

    # 2. Build requirements text payload
    requirements_text = "\n".join(f"[{r.type}] {r.description}" for r in requirements)

    # 3. Call AI Service with error handling
    try:
        uml_output = generate_uml_from_requirements(
            requirements_text,
            project.model_provider,
            project.model_name,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"UML generation failed: {str(e)}",
        )

    if not uml_output or not uml_output.strip():
        raise HTTPException(
            status_code=502,
            detail="UML generation returned empty output.",
        )

    return uml_output