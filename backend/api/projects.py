from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import get_db
from models import User, Project
from .dependencies import get_current_user
from services.llm_client import AVAILABLE_MODELS, DEFAULT_PROVIDER, DEFAULT_MODEL, validate_model

router = APIRouter()


class ProjectCreate(BaseModel):
    app_name: str
    model_provider: str = DEFAULT_PROVIDER
    model_name: str = DEFAULT_MODEL


class ProjectModelUpdate(BaseModel):
    model_provider: str
    model_name: str


class ProjectResponse(BaseModel):
    id: int
    app_name: str
    created_at: datetime
    requirement_count: int
    model_provider: str
    model_name: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    result = []
    for p in projects:
        active_count = sum(1 for r in p.requirements if r.is_active)
        result.append(
            ProjectResponse(
                id=p.id,
                app_name=p.app_name,
                created_at=p.created_at,
                requirement_count=active_count,
                model_provider=p.model_provider,
                model_name=p.model_name,
            )
        )
    return result


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        validate_model(project_data.model_provider, project_data.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project = Project(
        user_id=current_user.id,
        app_name=project_data.app_name,
        model_provider=project_data.model_provider,
        model_name=project_data.model_name,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=project.id,
        app_name=project.app_name,
        created_at=project.created_at,
        requirement_count=0,
        model_provider=project.model_provider,
        model_name=project.model_name,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    active_count = sum(1 for r in project.requirements if r.is_active)
    return ProjectResponse(
        id=project.id,
        app_name=project.app_name,
        created_at=project.created_at,
        requirement_count=active_count,
        model_provider=project.model_provider,
        model_name=project.model_name,
    )


@router.patch("/{project_id}/model", response_model=ProjectResponse)
def update_project_model(
    project_id: int,
    update: ProjectModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        validate_model(update.model_provider, update.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.model_provider = update.model_provider
    project.model_name = update.model_name
    db.commit()
    db.refresh(project)
    active_count = sum(1 for r in project.requirements if r.is_active)
    return ProjectResponse(
        id=project.id,
        app_name=project.app_name,
        created_at=project.created_at,
        requirement_count=active_count,
        model_provider=project.model_provider,
        model_name=project.model_name,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
