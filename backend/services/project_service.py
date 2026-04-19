from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Project
from schemas.project import ProjectCreate, ProjectModelUpdate
from services.llm_client import validate_model

def get_active_requirement_count(project: Project) -> int:
    """Calculates the number of active requirements in a project."""
    return sum(1 for r in project.requirements if r.is_active)

def list_user_projects(db: Session, user_id: int):
    """Returns a list of all projects belonging to a specific user."""
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )

def create_project(db: Session, user_id: int, data: ProjectCreate):
    """Validates AI model and creates a new project record."""
    try:
        validate_model(data.model_provider, data.model_name)
    except ValueError as e:
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

def get_project_by_id(db: Session, project_id: int, user_id: int):
    """Fetches a single project if it belongs to the user, else raises 404."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def update_model_settings(db: Session, project_id: int, user_id: int, update: ProjectModelUpdate):
    """Validates and updates the AI model settings for a project."""
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

def delete_user_project(db: Session, project_id: int, user_id: int):
    """Permanently deletes a project from the database."""
    project = get_project_by_id(db, project_id, user_id)
    db.delete(project)
    db.commit()