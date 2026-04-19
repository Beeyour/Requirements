from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from .dependencies import get_current_user
from schemas.project import ProjectCreate, ProjectModelUpdate, ProjectResponse
from services import project_service

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves all projects owned by the authenticated user."""
    projects = project_service.list_user_projects(db, current_user.id)
    return [
        ProjectResponse(
            **p.__dict__, 
            requirement_count=project_service.get_active_requirement_count(p)
        ) for p in projects
    ]

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a new software requirement project."""
    project = project_service.create_project(db, current_user.id, project_data)
    return ProjectResponse(
        **project.__dict__,
        requirement_count=0
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves detailed information about a specific project."""
    project = project_service.get_project_by_id(db, project_id, current_user.id)
    return ProjectResponse(
        **project.__dict__,
        requirement_count=project_service.get_active_requirement_count(project)
    )

@router.patch("/{project_id}/model", response_model=ProjectResponse)
def update_project_model(
    project_id: int,
    update: ProjectModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates the AI model and provider for an existing project."""
    project = project_service.update_model_settings(db, project_id, current_user.id, update)
    return ProjectResponse(
        **project.__dict__,
        requirement_count=project_service.get_active_requirement_count(project)
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes a project and its associated data."""
    project_service.delete_user_project(db, project_id, current_user.id)