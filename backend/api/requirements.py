from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

# Absolute imports for consistent package resolution
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
    # Verify project ownership before triggering the AI SRS generation
    project = requirement_service.get_project_or_403(db, request.project_id, current_user.id)
    
    # Await the async service because it triggers the LLM agent
    # Returns a list of generated requirements
    return await requirement_service.generate_srs_from_chat(db, project)

@router.get("/{project_id}", response_model=List[RequirementResponse])
def get_requirements(
    project_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization check and retrieval of active/inactive requirements
    requirement_service.get_project_or_403(db, project_id, current_user.id)
    
    # Fetches requirements directly from the database
    return requirement_service.get_project_requirements(db, project_id, include_inactive)

@router.put("/update-requirement/{requirement_id}", response_model=UpdateRequirementResponse)
async def update_requirement(
    requirement_id: int,
    request: UpdateRequirementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Await the async service that updates requirement and checks for AI conflicts
    new_req, conflict_report = await requirement_service.update_existing_requirement(
        db, requirement_id, current_user.id, request
    )
    
    # Return formatted response including potential AI feedback
    return {
        "requirement": new_req,
        "conflict_report": conflict_report if conflict_report.get("has_conflicts") else None
    }
