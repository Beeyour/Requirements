from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.user import User
from backend.api.dependencies import get_current_user
from backend.schemas.requirement import (
    RequirementResponse,
    GenerateSRSRequest,
    UpdateRequirementRequest,
    UpdateRequirementResponse
)
from backend.services import requirement_service

router = APIRouter()

@router.post("/generate-srs", response_model=List[RequirementResponse])
async def generate_srs(
    request: GenerateSRSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = requirement_service.get_project_or_403(db, request.project_id, current_user.id)
    return await requirement_service.generate_srs_from_chat(db, project)

@router.get("/{project_id}", response_model=List[RequirementResponse])
def get_requirements(
    project_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requirement_service.get_project_or_403(db, project_id, current_user.id)
    return requirement_service.get_project_requirements(db, project_id, include_inactive)

@router.post("/update-requirements/{project_id}", response_model=List[RequirementResponse])
async def update_requirements(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = requirement_service.get_project_or_403(db, project_id, current_user.id)
    # archive old ones first, then regenerate from current chat history
    await requirement_service.archive_existing_requirements(db, project_id)
    return await requirement_service.generate_srs_from_chat(db, project)

@router.put("/update-requirement/{requirement_id}", response_model=UpdateRequirementResponse)
async def update_requirement(
    requirement_id: int,
    request: UpdateRequirementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_req, conflict_report = await requirement_service.update_existing_requirement(
        db, requirement_id, current_user.id, request
    )
    # only surface conflict_report when there are actual conflicts
    return {
        "requirement": new_req,
        "conflict_report": conflict_report if conflict_report.get("has_conflicts") else None
    }
