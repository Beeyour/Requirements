from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import get_db
from models import User, Project, Requirement
from .dependencies import get_current_user
from services.ai_agent import generate_uml_from_requirements

router = APIRouter()


class UMLResponse(BaseModel):
    project_id: int
    uml_output: str
    generated_at: datetime

    class Config:
        from_attributes = True

def _get_project_or_404(db, project_id, user_id):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/generate-uml", response_model=UMLResponse)
def generate_uml(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id, current_user.id)

    # Fetch ONLY active requirements for this project — no other context
    requirements: List[Requirement] = (
        db.query(Requirement)
        .filter(
            Requirement.project_id == project_id,
            Requirement.is_active == True,
        )
        .order_by(Requirement.type, Requirement.id)
        .all()
    )

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="No active requirements found for this project. Generate SRS first.",
        )

    # Build isolated requirements text payload
    requirements_text = "\n".join(
        f"[{r.type}] {r.description}" for r in requirements
    )

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

    return UMLResponse(
        project_id=project_id,
        uml_output=uml_output,
        generated_at=datetime.utcnow(),
    )
