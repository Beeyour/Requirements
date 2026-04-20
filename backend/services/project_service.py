from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectModelUpdate
from backend.services.llm.utils import validate_model

def get_active_requirement_count(project: Project) -> int:
    """
    Calculates the total number of requirements marked as active for a given project.
    """
    if not project.requirements:
        return 0
    return sum(1 for r in project.requirements if r.is_active)

def list_user_projects(db: Session, user_id: int) -> List[Project]:
    """
    Returns all projects belonging to a specific user, sorted by creation date (newest first).
    """
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )

def create_project(db: Session, user_id: int, data: ProjectCreate) -> Project:
    """
    Validates model settings and creates a new project record in the database.
    Note: Timestamps (created_at) are handled automatically by the DB defaults.
    """
    # 1. Validate the AI model and provider settings
    try:
        validate_model(data.model_provider, data.model_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 2. Map Schema fields (app_name) to Model fields (name)
    db_project = Project(
        user_id=user_id,
        name=data.app_name,  # 'app_name' from user input maps to 'name' in DB
        model_provider=data.model_provider,
        model_name=data.model_name,
    )

    # 3. Save to database
    db.add(db_project)
    db.commit()
    
    # 4. Refresh to load the auto-generated fields like 'id' and 'created_at'
    db.refresh(db_project)
    return db_project

def get_project_by_id(db: Session, project_id: int, user_id: int) -> Project:
    """
    Fetches a project by ID and ensures the user has permission to access it.
    """
    project = db.query(Project).filter(
        Project.id == project_id, 
        Project.user_id == user_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project

def update_model_settings(db: Session, project_id: int, user_id: int, update: ProjectModelUpdate) -> Project:
    """
    Validates and updates the LLM configuration for an existing project.
    """
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
    """
    Permanently removes a project record from the database.
    """
    project = get_project_by_id(db, project_id, user_id)
    db.delete(project)
    db.commit()