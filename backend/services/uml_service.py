from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from models import Project
from models import Requirement
from services import generate_uml_from_requirements


def get_project_or_404(db: Session, project_id: int, user_id: int) -> Project:
    # Ensure the user actually owns this project before proceeding
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")

    return project


def process_uml_generation(db: Session, project: Project) -> str:
    # 1. Retrieve only active requirements for the given project
    requirements = (
        db.query(Requirement)
        .filter(Requirement.project_id == project.id, Requirement.is_active == True)
        .order_by(Requirement.type, Requirement.id)
        .all()
    )

    if not requirements:
        raise HTTPException(status_code=400, detail="No active requirements found. Generate SRS first.")

    # 2. Format requirements into a clean text block for the LLM prompt
    requirements_text = "\n".join(f"[{r.type}] {r.description}" for r in requirements)

    # 3. Call the AI service and handle potential API failures (e.g., timeout, rate limits)
    try:
        uml_output = generate_uml_from_requirements(
            requirements_text,
            project.model_provider,
            project.model_name,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"UML generation failed: {str(e)}")

    # Ensure the AI didn't return a blank response
    if not uml_output or not uml_output.strip():
        raise HTTPException(status_code=502, detail="UML generation returned empty output.")

    return uml_output