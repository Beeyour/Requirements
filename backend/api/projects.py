from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Absolute imports for reliability within Docker
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

    # Fetch all projects for the authenticated user and calculate requirement counts.

    # 1. Retrieve raw project models from the database
    projects = project_service.list_user_projects(db, current_user.id)

    # 2. Manually construct ProjectResponse to include the calculated requirement_count
    # and map database fields correctly to the schema.
    results = []
    for p in projects:
        count = project_service.get_active_requirement_count(p)
        
        # Note: Mapping 'name' from DB to 'app_name' in Schema if they differ
        res = ProjectResponse(
            id=p.id,
            app_name=p.name,  # Mapping DB 'name' to Schema 'app_name'
            model_provider=p.model_provider,
            model_name=p.model_name,
            created_at=p.created_at,
            updated_at=p.updated_at if hasattr(p, 'updated_at') else p.created_at,
            requirement_count=count
        )
        results.append(res)
    
    return results

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Initializes a new project and returns it with auto-generated timestamps.
    """
    # استدعاء السيرفس
    project = project_service.create_project(db, current_user.id, project_data)
    
    # بناء الرد الراجع للمتصفح
    return ProjectResponse(
        id=project.id,
        app_name=project.app_name, 
        model_provider=project.model_provider,
        model_name=project.model_name,
        created_at=project.created_at, 
        updated_at=project.created_at,
        requirement_count=0
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Retrieve details for a specific project.

    project = project_service.get_project_by_id(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    count = project_service.get_active_requirement_count(project)
    
    return ProjectResponse(
        id=project.id,
        app_name=project.name,
        model_provider=project.model_provider,
        model_name=project.model_name,
        created_at=project.created_at,
        updated_at=project.updated_at,
        requirement_count=count
    )

@router.patch("/{project_id}/model", response_model=ProjectResponse)
def update_project_model(
    project_id: int,
    update: ProjectModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Update the LLM settings for an existing project.

    project = project_service.update_model_settings(db, project_id, current_user.id, update)
    count = project_service.get_active_requirement_count(project)
    
    return ProjectResponse(
        id=project.id,
        app_name=project.name,
        model_provider=project.model_provider,
        model_name=project.model_name,
        created_at=project.created_at,
        updated_at=datetime.utcnow(), # Manually updating the timestamp for immediate feedback
        requirement_count=count
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Delete a project and its associated data.

    project_service.delete_user_project(db, project_id, current_user.id)
    return None