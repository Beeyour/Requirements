from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import Project, ConversationHistory
from typing import List
from services.ai_agent import get_interview_response, check_saturation, get_initial_greeting

def get_project_or_404(db: Session, project_id: int, user_id: int):
    """Retrieves a project or raises 404 if not found or unauthorized."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def get_active_history(db: Session, project_id: int) -> List[ConversationHistory]:
    """Fetches non-archived messages for a specific project."""
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
    """Formats a DB model instance into a response-friendly dictionary."""
    return {
        "id": msg.id,
        "role": msg.role,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat(),
    }

def start_new_interview(db: Session, project: Project):
    """Initializes the chat with an AI greeting if no history exists."""
    existing = get_active_history(db, project.id)
    if existing:
        return format_message(existing[-1])

    greeting_content = get_initial_greeting(
        project.app_name,
        project.model_provider,
        project.model_name,
    )
    
    new_msg = ConversationHistory(project_id=project.id, role="assistant", content=greeting_content)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return format_message(new_msg)

def process_chat_message(db: Session, project: Project, content: str):
    """Handles user message, AI response generation, and saturation check."""
    # 1. Save user message
    user_msg = ConversationHistory(project_id=project.id, role="user", content=content)
    db.add(user_msg)
    db.commit()

    # 2. Prepare context for AI
    all_msgs = get_active_history(db, project.id)
    context = [{"role": m.role, "content": m.content} for m in all_msgs]
    
    # 3. Get AI response and saturation status
    ai_resp = get_interview_response(context[-10:], project.app_name, project.model_provider, project.model_name)
    saturation = check_saturation(context, project.model_provider, project.model_name)

    # 4. Save assistant response
    assistant_msg = ConversationHistory(
        project_id=project.id, role="assistant", content=ai_resp["message"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return {
        "message": ai_resp["message"],
        "is_saturated": saturation.get("is_saturated", False),
        "message_id": assistant_msg.id,
        "history": [format_message(m) for m in get_active_history(db, project.id)]
    }

def archive_chat_history(db: Session, project_id: int):
    """Soft-deletes (archives) all active messages for a project."""
    db.query(ConversationHistory).filter(
        ConversationHistory.project_id == project_id,
        ConversationHistory.is_archived == False,
    ).update({"is_archived": True})
    db.commit()