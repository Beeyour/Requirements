from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Project, ConversationHistory, Requirement, RequirementLog
from schemas.requirement import UpdateRequirementRequest
from services.ai_agent import generate_requirements_from_conversation, detect_conflicts
from datetime import datetime

def get_project_or_403(db: Session, project_id: int, user_id: int):
    """Checks if project exists and belongs to the user."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def get_project_requirements(db: Session, project_id: int, include_inactive: bool = False):
    """Retrieves list of requirements for a project."""
    query = db.query(Requirement).filter(Requirement.project_id == project_id)
    if not include_inactive:
        query = query.filter(Requirement.is_active == True)
    return query.order_by(Requirement.type, Requirement.id).all()

def generate_srs_from_chat(db: Session, project: Project):
    """Converts active chat history into structured requirements using AI."""
    messages = db.query(ConversationHistory).filter(
        ConversationHistory.project_id == project.id,
        ConversationHistory.is_archived == False
    ).order_by(ConversationHistory.timestamp.asc()).all()

    if not messages:
        raise HTTPException(status_code=400, detail="No conversation history found")

    conversation = [{"role": m.role, "content": m.content} for m in messages]
    generated = generate_requirements_from_conversation(
        conversation, project.app_name, project.model_provider, project.model_name
    )

    created_requirements = []
    # Process both Functional and Non-Functional items
    for req_type in ["functional", "non_functional"]:
        label = "Functional" if req_type == "functional" else "Non-Functional"
        for item in generated.get(req_type, []):
            req = Requirement(
                project_id=project.id,
                type=label,
                description=item["description"],
                version_number=1,
                is_active=True
            )
            db.add(req)
            db.flush() # Get ID before commit
            db.add(RequirementLog(requirement_id=req.id, change_reason="Initial SRS generation"))
            created_requirements.append(req)
    
    db.commit()
    return created_requirements

def update_existing_requirement(db: Session, requirement_id: int, user_id: int, data: UpdateRequirementRequest):
    """Deactivates old requirement and creates a new version with conflict detection."""
    old_req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not old_req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    project = get_project_or_403(db, old_req.project_id, user_id)

    # Versioning: Mark old as inactive
    old_req.is_active = False
    db.flush()

    # Create new version
    new_req = Requirement(
        project_id=old_req.project_id,
        type=old_req.type,
        description=data.description,
        version_number=old_req.version_number + 1,
        is_active=True
    )
    db.add(new_req)
    db.flush()
    db.add(RequirementLog(
        requirement_id=new_req.id,
        change_reason=data.change_reason or "Manual edit",
        timestamp=datetime.utcnow()
    ))
    db.commit()
    db.refresh(new_req)

    # AI Conflict Detection logic
    active_reqs = db.query(Requirement).filter(
        Requirement.project_id == new_req.project_id, 
        Requirement.is_active == True
    ).all()
    
    reqs_list = [{"id": r.id, "type": r.type, "description": r.description} for r in active_reqs]
    edited_item = {"id": new_req.id, "type": new_req.type, "description": new_req.description}

    conflict_report = detect_conflicts(edited_item, reqs_list, project.model_provider, project.model_name)
    
    return new_req, conflict_report