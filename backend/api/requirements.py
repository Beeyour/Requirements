from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime
from database import get_db
from models import User, Project, ConversationHistory, Requirement, RequirementLog
from .dependencies import get_current_user
from services.ai_agent import generate_requirements_from_conversation, detect_conflicts

router = APIRouter()


class RequirementResponse(BaseModel):
    id: int
    project_id: int
    type: str
    description: str
    version_number: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateSRSRequest(BaseModel):
    project_id: int


class UpdateRequirementRequest(BaseModel):
    description: str
    change_reason: Optional[str] = None


class UpdateRequirementResponse(BaseModel):
    requirement: RequirementResponse
    conflict_report: Optional[Dict[str, Any]] = None


def _req_response(r: Requirement) -> RequirementResponse:
    return RequirementResponse(
        id=r.id,
        project_id=r.project_id,
        type=r.type,
        description=r.description,
        version_number=r.version_number,
        is_active=r.is_active,
        created_at=r.created_at,
    )


def _get_project_or_403(db, project_id, user_id):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/generate-srs", response_model=List[RequirementResponse])
def generate_srs(
    request: GenerateSRSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_403(db, request.project_id, current_user.id)

    messages = (
        db.query(ConversationHistory)
        .filter(
            ConversationHistory.project_id == request.project_id,
            ConversationHistory.is_archived == False,
        )
        .order_by(ConversationHistory.timestamp.asc())
        .all()
    )
    if not messages:
        raise HTTPException(status_code=400, detail="No conversation history found")

    conversation = [{"role": m.role, "content": m.content} for m in messages]
    generated = generate_requirements_from_conversation(
        conversation,
        project.app_name,
        project.model_provider,
        project.model_name,
    )

    created: List[Requirement] = []
    for item in generated.get("functional", []):
        req = Requirement(
            project_id=request.project_id,
            type="Functional",
            description=item["description"],
            version_number=1,
            is_active=True,
        )
        db.add(req)
        db.flush()
        db.add(RequirementLog(requirement_id=req.id, change_reason="Initial SRS generation"))
        created.append(req)

    for item in generated.get("non_functional", []):
        req = Requirement(
            project_id=request.project_id,
            type="Non-Functional",
            description=item["description"],
            version_number=1,
            is_active=True,
        )
        db.add(req)
        db.flush()
        db.add(RequirementLog(requirement_id=req.id, change_reason="Initial SRS generation"))
        created.append(req)

    db.commit()
    for r in created:
        db.refresh(r)
    return [_req_response(r) for r in created]


@router.get("/requirements/{project_id}", response_model=List[RequirementResponse])
def get_requirements(
    project_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_403(db, project_id, current_user.id)
    query = db.query(Requirement).filter(Requirement.project_id == project_id)
    if not include_inactive:
        query = query.filter(Requirement.is_active == True)
    return [_req_response(r) for r in query.order_by(Requirement.type, Requirement.id).all()]


@router.put("/update-requirement/{requirement_id}", response_model=UpdateRequirementResponse)
def update_requirement(
    requirement_id: int,
    request: UpdateRequirementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    old_req = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not old_req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    project = _get_project_or_403(db, old_req.project_id, current_user.id)

    old_req.is_active = False
    db.flush()

    new_req = Requirement(
        project_id=old_req.project_id,
        type=old_req.type,
        description=request.description,
        version_number=old_req.version_number + 1,
        is_active=True,
    )
    db.add(new_req)
    db.flush()
    db.add(
        RequirementLog(
            requirement_id=new_req.id,
            change_reason=request.change_reason or "Manual edit",
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()
    db.refresh(new_req)

    active_reqs = (
        db.query(Requirement)
        .filter(Requirement.project_id == new_req.project_id, Requirement.is_active == True)
        .all()
    )
    reqs_list = [{"id": r.id, "type": r.type, "description": r.description} for r in active_reqs]
    edited = {"id": new_req.id, "type": new_req.type, "description": new_req.description}

    conflict_report = detect_conflicts(
        edited,
        reqs_list,
        project.model_provider,
        project.model_name,
    )

    return UpdateRequirementResponse(
        requirement=_req_response(new_req),
        conflict_report=conflict_report if conflict_report.get("has_conflicts") else None,
    )
