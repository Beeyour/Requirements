from sqlalchemy.orm import Session
from datetime import timezone
from fastapi import HTTPException
from backend.models import Project, ConversationHistory
from typing import List
# Note: Ensure imports match your project structure
from backend.services.ai_agent import get_interview_response, check_saturation, get_initial_greeting

def get_project_or_404(db: Session, project_id: int, user_id: int):
    # Standard sync DB query
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def get_active_history(db: Session, project_id: int) -> List[ConversationHistory]:
    # Standard sync DB query
    return (
        db.query(ConversationHistory)
        .filter(
            ConversationHistory.project_id == project_id,
            ConversationHistory.is_archived == False,
        )
        .order_by(ConversationHistory.timestamp.asc())
        .all()
    )

def format_message(msg: ConversationHistory):
    # ensure the timestamp is on UTC format
    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None, 
    }

async def start_new_interview(db: Session, project: Project):
    # Changed to 'async' to allow 'awaiting' the AI greeting
    existing = get_active_history(db, project.id)
    if existing:
        return format_message(existing[-1])

    # Added 'await' for the AI call
    greeting_content = await get_initial_greeting(
        project.app_name,
        project.model_provider,
        project.model_name,
    )
    
    new_msg = ConversationHistory(project_id=project.id, role="assistant", content=greeting_content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return format_message(new_msg)

async def process_chat_message(db: Session, project: Project, content: str):
    # Changed to 'async' to support non-blocking AI calls
    
    # 1. Save user message (Sync DB)
    user_msg = ConversationHistory(project_id=project.id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    # 2. Prepare context
    all_msgs = get_active_history(db, project.id)
    context = [{"role": m.role, "content": m.content} for m in all_msgs]
    
    # 3. Get AI JSON-structured response (using recent context for efficiency)
    ai_resp = await get_interview_response(
        context[-10:], 
        project.app_name, 
        project.model_provider, 
        project.model_name
    )
    saturation_flag = bool(ai_resp.get("is_saturated", False))
    if not saturation_flag:
        saturation = await check_saturation(
            context,
            project.model_provider,
            project.model_name
        )
        saturation_flag = bool(saturation.get("is_saturated", False))

    # 4. Save AI response (Sync DB)
    assistant_msg = ConversationHistory(
        project_id=project.id, role="assistant", content=ai_resp["message"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Return structure remains identical for frontend compatibility
    return {
        "message": ai_resp["message"],
        "is_saturated": saturation_flag,
        "message_id": assistant_msg.id,
        "history": [format_message(m) for m in get_active_history(db, project.id)]
    }

def archive_chat_history(db: Session, project_id: int):
    # Soft-delete logic remains sync
    db.query(ConversationHistory).filter(
        ConversationHistory.project_id == project_id,
        ConversationHistory.is_archived == False,
    ).update({"is_archived": True})
    db.commit()