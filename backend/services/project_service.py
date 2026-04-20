from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectModelUpdate
from backend.services.llm_client import validate_model

def get_active_requirement_count(project: Project) -> int:
    # Calculates the total number of requirements marked as active for the project
    return sum(1 for r in project.requirements if r.is_active)

def list_user_projects(db: Session, user_id: int) -> List[Project]:
    # Returns all projects for a user, sorted by the most recently created
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )

def create_project(db: Session, user_id: int, data: ProjectCreate) -> Project:
    # Validate the AI model/provider before creating the database record
    try:
        validate_model(data.model_provider, data.model_name)
    except ValueError as e:
        # Standard 400 error helps frontend show validation messages
        raise HTTPException(status_code=400, detail=str(e))
    
    db_project = Project(
        user_id=user_id,
        app_name=data.app_name,
        model_provider=data.model_provider,
        model_name=data.model_name,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project_by_id(db: Session, project_id: int, user_id: int) -> Project:
    # Fetch project or raise 404; also ensures user authorization (ownership check)
    project = db.query(Project).filter(
        Project.id == project_id, 
        Project.user_id == user_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project

def update_model_settings(db: Session, project_id: int, user_id: int, update: ProjectModelUpdate) -> Project:
    # Ensure the new model configuration is supported before updating
    try:
        validate_model(update.model_provider, update.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project = get_project_by_id(db, project_id, user_id)
    project.model_provider = update.model_provider
    project.model_name = update.model_name

    db.commit()
    db.refresh(project)
    return project

def delete_user_project(db: Session, project_id: int, user_id: int) -> None:
    # Permanently delete the project and all its cascading child entities
    project = get_project_by_id(db, project_id, user_id)
    db.delete(project)
    db.commit()