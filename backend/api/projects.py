from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.user import User
from backend.api.dependencies import get_current_user
from backend.schemas.project import ProjectCreate, ProjectModelUpdate, ProjectResponse
from backend.services import project_service

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetches all projects associated with the logged-in user
    projects = project_service.list_user_projects(db, current_user.id)
    
    # Enrich the response with the calculated count of active requirements
    return [
        ProjectResponse(
            **ProjectResponse.model_validate(p).model_dump(), 
            requirement_count=project_service.get_active_requirement_count(p)
        ) for p in projects
    ]

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Initializes a new project and binds it to the current user
    project = project_service.create_project(db, current_user.id, project_data)
    
    # New projects start with zero requirements
    return ProjectResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        requirement_count=0
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Retrieve a specific project's details with its requirement statistics
    project = project_service.get_project_by_id(db, project_id, current_user.id)
    return ProjectResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        requirement_count=project_service.get_active_requirement_count(project)
    )

@router.patch("/{project_id}/model", response_model=ProjectResponse)
def update_project_model(
    project_id: int,
    update: ProjectModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Allows switching the underlying LLM engine for the project on-the-fly
    project = project_service.update_model_settings(db, project_id, current_user.id, update)
    return ProjectResponse(
        **ProjectResponse.model_validate(project).model_dump(),
        requirement_count=project_service.get_active_requirement_count(project)
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Permanent deletion of the project and its cascading children (requirements/logs)
    project_service.delete_user_project(db, project_id, current_user.id)