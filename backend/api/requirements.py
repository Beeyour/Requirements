from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from .dependencies import get_current_user
from schemas.requirement import RequirementResponse, GenerateSRSRequest, UpdateRequirementRequest, UpdateRequirementResponse
from services import requirement_service

router = APIRouter()

@router.post("/generate-srs", response_model=List[RequirementResponse])
def generate_srs(
    request: GenerateSRSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers AI agent to generate SRS from the current conversation."""
    project = requirement_service.get_project_or_403(db, request.project_id, current_user.id)
    return requirement_service.generate_srs_from_chat(db, project)

@router.get("/{project_id}", response_model=List[RequirementResponse])
def get_requirements(
    project_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists all requirements (Active by default) for a project."""
    requirement_service.get_project_or_403(db, project_id, current_user.id)
    return requirement_service.get_project_requirements(db, project_id, include_inactive)

@router.put("/update-requirement/{requirement_id}", response_model=UpdateRequirementResponse)
def update_requirement(
    requirement_id: int,
    request: UpdateRequirementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates a requirement and returns potential AI-detected conflicts."""
    new_req, conflict_report = requirement_service.update_existing_requirement(
        db, requirement_id, current_user.id, request
    )
    
    return {
        "requirement": new_req,
        "conflict_report": conflict_report if conflict_report.get("has_conflicts") else None
    }