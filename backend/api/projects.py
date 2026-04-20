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
    current_user: User = Depends(get_db),
):
    projects = project_service.list_user_projects(db, current_user.id)


    return [
        ProjectResponse.model_validate(
            p, 
            update={"requirement_count": project_service.get_active_requirement_count(p)}
        ) for p in projects
    ]

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_service.create_project(db, current_user.id, project_data)
    

    return ProjectResponse.model_validate(project, update={"requirement_count": 0})

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_service.get_project_by_id(db, project_id, current_user.id)
    count = project_service.get_active_requirement_count(project)
    
    return ProjectResponse.model_validate(project, update={"requirement_count": count})

@router.patch("/{project_id}/model", response_model=ProjectResponse)
def update_project_model(
    project_id: int,
    update: ProjectModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_service.update_model_settings(db, project_id, current_user.id, update)
    count = project_service.get_active_requirement_count(project)
    
    return ProjectResponse.model_validate(project, update={"requirement_count": count})