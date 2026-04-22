<<<<<<< HEAD
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
<<<<<<< HEAD
from backend.database import get_db
from backend.models.user import User
from backend.api.dependencies import get_current_user
from backend.schemas.chat import MessageResponse, ChatRequest, ChatResponse, ResetRequest
from backend.services import chat_service

router = APIRouter()

@router.post("/chat/{project_id}/start", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
=======
from database import get_db
from models import User, Project, ConversationHistory
from .dependencies import get_current_user
from services.ai_agent import get_interview_response, check_saturation, get_initial_greeting
from datetime import datetime, timezone

router = APIRouter()


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    project_id: int
    content: str


class ChatResponse(BaseModel):
    message: str
    is_saturated: bool
    message_id: int
    history: List[MessageResponse]


def _active_history(db: Session, project_id: int) -> List[ConversationHistory]:
    return (
        db.query(ConversationHistory)
        .filter(
            ConversationHistory.project_id == project_id,
            ConversationHistory.is_archived == False,
        )
        .order_by(ConversationHistory.timestamp.asc())
        .all()
    )


def _to_response(msg: ConversationHistory) -> MessageResponse:
    ts = msg.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    
    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        timestamp=ts,
    )


def _get_project_or_404(db, project_id, user_id):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/chat/{project_id}/start", response_model=MessageResponse)
def start_interview(
>>>>>>> e95e62c (try to solve the history time issue by change the logic on backend)
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Changed to 'async' and added 'await' because this triggers an AI call
    project = chat_service.get_project_or_404(db, project_id, current_user.id)
    return await chat_service.start_new_interview(db, project)

@router.get("/chat/{project_id}/history", response_model=List[MessageResponse])
def get_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # This remains 'def' because it only performs synchronous DB queries
    chat_service.get_project_or_404(db, project_id, current_user.id)
    history = chat_service.get_active_history(db, project_id)
    return history

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Changed to 'async' and added 'await' because AI processing is now non-blocking
    project = chat_service.get_project_or_404(db, request.project_id, current_user.id)
    return await chat_service.process_chat_message(db, project, request.content)

@router.post("/chat/reset", status_code=status.HTTP_200_OK)
def reset_chat(
    request: ResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # This remains 'def' (synchronous) as it only updates database flags
    chat_service.get_project_or_404(db, request.project_id, current_user.id)
    chat_service.archive_chat_history(db, request.project_id)
    return {
        "message": "Conversation archived successfully",
        "project_id": request.project_id
    }
=======
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
from models import User, Project, ConversationHistory
from .dependencies import get_current_user
from services.ai_agent import get_interview_response, check_saturation, get_initial_greeting
from datetime import datetime, timezone

router = APIRouter()


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    project_id: int
    content: str


class ChatResponse(BaseModel):
    message: str
    is_saturated: bool
    message_id: int
    history: List[MessageResponse]


def _active_history(db: Session, project_id: int) -> List[ConversationHistory]:
    return (
        db.query(ConversationHistory)
        .filter(
            ConversationHistory.project_id == project_id,
            ConversationHistory.is_archived == False,
        )
        .order_by(ConversationHistory.timestamp.asc())
        .all()
    )


def _to_response(msg: ConversationHistory) -> MessageResponse:
    ts = msg.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    
    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        timestamp=ts,
    )


def _get_project_or_404(db, project_id, user_id):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/chat/{project_id}/start", response_model=MessageResponse)
def start_interview(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id, current_user.id)

    existing = _active_history(db, project_id)
    if existing:
        return _to_response(existing[-1])

    greeting = get_initial_greeting(
        project.app_name,
        project.model_provider,
        project.model_name,
    )
    msg = ConversationHistory(project_id=project_id, role="assistant", content=greeting)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _to_response(msg)


@router.get("/chat/{project_id}/history", response_model=List[MessageResponse])
def get_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    return [_to_response(m) for m in _active_history(db, project_id)]


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, request.project_id, current_user.id)

    user_msg = ConversationHistory(
        project_id=request.project_id, role="user", content=request.content
    )
    db.add(user_msg)
    db.commit()

    all_msgs = _active_history(db, request.project_id)
    context = [{"role": m.role, "content": m.content} for m in all_msgs]
    recent_context = context[-10:]

    ai_resp = get_interview_response(
        recent_context,
        project.app_name,
        project.model_provider,
        project.model_name,
    )
    saturation = check_saturation(context, project.model_provider, project.model_name)

    assistant_msg = ConversationHistory(
        project_id=request.project_id, role="assistant", content=ai_resp["message"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    full_history = _active_history(db, request.project_id)

    return ChatResponse(
        message=ai_resp["message"],
        is_saturated=saturation.get("is_saturated", False),
        message_id=assistant_msg.id,
        history=[_to_response(m) for m in full_history],
    )


class ResetRequest(BaseModel):
    project_id: int


@router.post("/chat/reset")
def reset_chat(
    request: ResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, request.project_id, current_user.id)
    db.query(ConversationHistory).filter(
        ConversationHistory.project_id == request.project_id,
        ConversationHistory.is_archived == False,
    ).update({"is_archived": True})
    db.commit()
    return {"message": "Conversation archived. Previous requirements remain accessible."}
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
