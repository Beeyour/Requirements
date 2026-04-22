from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any

# Absolute imports for package reliability
from backend.models.project import Project
from backend.models.conversation import ConversationHistory
from backend.models.requirement import Requirement
from backend.models.requirement_log import RequirementLog
from backend.schemas.requirement import UpdateRequirementRequest
# Simplified import from the agent package root
from backend.services.ai_agent import generate_requirements_from_conversation, detect_conflicts

def get_project_or_403(db: Session, project_id: int, user_id: int) -> Project:
    # Authorization and existence check for projects
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")
    return project

def get_project_requirements(db: Session, project_id: int, include_inactive: bool = False) -> List[Requirement]:
    # Retrieve project requirements with optional filtering
    query = db.query(Requirement).filter(Requirement.project_id == project_id)
    if not include_inactive:
        query = query.filter(Requirement.is_active == True)
    return query.order_by(Requirement.type, Requirement.id).all()

async def generate_srs_from_chat(db: Session, project: Project) -> List[Requirement]:
    # Extracts active chat history and uses AI to structure requirements (Async)
    messages = db.query(ConversationHistory).filter(
        ConversationHistory.project_id == project.id,
        ConversationHistory.is_archived == False
    ).order_by(ConversationHistory.timestamp.asc()).all()

    if not messages:
        raise HTTPException(status_code=400, detail="No conversation history available")

    # Map database models to basic dictionary format
    conversation = [{"role": m.role, "content": m.content} for m in messages]

    # Trigger AI generation (Already converted to async in our previous steps)
    generated = await generate_requirements_from_conversation(
        conversation, project.app_name, project.model_provider, project.model_name
    )

    created_requirements = []
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
            db.flush() 

            db.add(RequirementLog(requirement_id=req.id, change_reason="Initial SRS generation"))
            created_requirements.append(req)

    db.commit()
    return created_requirements

async def update_existing_requirement(
    db: Session, 
    requirement_id: int, 
    user_id: int, 
    data: UpdateRequirementRequest
) -> Tuple[Requirement, Dict[str, Any]]:
    # Implements versioning by deactivating old records and creating new ones
    old_req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not old_req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    project = get_project_or_403(db, old_req.project_id, user_id)

    old_req.is_active = False
    db.flush()

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
        timestamp=datetime.now(timezone.utc)
    ))
    db.commit()
    db.refresh(new_req)

    # Prepare data for Conflict Detection
    active_reqs = db.query(Requirement).filter(
        Requirement.project_id == new_req.project_id, 
        Requirement.is_active == True
    ).all()

    reqs_list = [{"id": r.id, "type": r.type, "description": r.description} for r in active_reqs]
    # Fixed: Removed the stray character at the end of this line
    edited_item = {"id": new_req.id, "type": new_req.type, "description": new_req.description}

    # Await AI analysis (Async compatible)
    conflict_report = await detect_conflicts(edited_item, reqs_list, project.model_provider, project.model_name)

    return new_req, conflict_report