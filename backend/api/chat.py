from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from .dependencies import get_current_user
from schemas.chat import MessageResponse, ChatRequest, ChatResponse, ResetRequest
from services import chat_service

router = APIRouter()

@router.post("/chat/{project_id}/start", response_model=MessageResponse)
def start_interview(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Initiates the requirement gathering interview."""
    project = chat_service.get_project_or_404(db, project_id, current_user.id)
    return chat_service.start_new_interview(db, project)

@router.get("/chat/{project_id}/history", response_model=List[MessageResponse])
def get_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves the active chat history for a project."""
    chat_service.get_project_or_404(db, project_id, current_user.id)
    history = chat_service.get_active_history(db, project_id)
    return [chat_service.format_message(m) for m in history]

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sends a user message and returns the AI assistant's response."""
    project = chat_service.get_project_or_404(db, request.project_id, current_user.id)
    return chat_service.process_chat_message(db, project, request.content)

@router.post("/chat/reset")
def reset_chat(
    request: ResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Archives the current conversation to start fresh."""
    chat_service.get_project_or_404(db, request.project_id, current_user.id)
    chat_service.archive_chat_history(db, request.project_id)
    return {"message": "Conversation archived. Previous requirements remain accessible."}