from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import requirement_service
from backend.services.uml import usecase_service
from backend.services.uml import class_digram_service
from backend.services.uml import activity_digram_service
from backend.services.uml import sequence_digram_service
from backend.services.llm.config import DEFAULT_PROVIDER, DEFAULT_MODEL


router = APIRouter()


def _get_formatted_requirements(project_id: int, db: Session) -> str:
    """Fetch and format requirements; raise 404 if none exist."""
    requirements = requirement_service.get_project_requirements(db, project_id, False)
    formatted = usecase_service.format_requirements_for_ai(requirements)
    if not formatted:
        raise HTTPException(status_code=404, detail="No active functional requirements found for this project.")
    return formatted


@router.get("/generate-usecase/{project_id}")
async def generate_usecase(project_id: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    result = await usecase_service.generate_usecase(
        db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    return result


@router.get("/generate-class/{project_id}")
async def generate_class(project_id: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    result = await class_digram_service.generate_class(
        db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    return result


@router.get("/generate-activity/{project_id}")
async def generate_activity(project_id: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    result = await activity_digram_service.generate_activity(
        db, project_id, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    return result


@router.get("/generate-sequence/{project_id}/{usecase_idx}")
async def generate_sequence(project_id: int, usecase_idx: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    result = await sequence_digram_service.generate_sequence(
        db, project_id, usecase_idx, formatted, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    return result