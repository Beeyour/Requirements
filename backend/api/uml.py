from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.api.dependencies import get_current_user
from backend.services import requirement_service
from backend.services.uml import usecase_service
from backend.services.uml import class_digram_service
from backend.services.uml import activity_digram_service
from backend.services.uml import sequence_digram_service
from backend.services.uml import utils
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

    usecase_json = await usecase_service.generate_usecase_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    puml_code = usecase_service.generate_plantuml(usecase_json, project_id)
    svg_url = utils.get_plantuml_svg(puml_code)

    return {"svg_url": svg_url, "plantuml_code": puml_code, "data": usecase_json}


@router.get("/generate-class/{project_id}")
async def generate_class(project_id: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    class_json = await class_digram_service.generate_class_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    puml_code = class_digram_service.generate_class_plantuml(class_json)
    svg_url = utils.get_plantuml_svg(puml_code)

    return {"svg_url": svg_url, "plantuml_code": puml_code, "data": class_json}


@router.get("/generate-activity/{project_id}")
async def generate_activity(project_id: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    # Activity diagram depends on existing Use Case + Class data
    usecase_json = await usecase_service.generate_usecase_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    class_json = await class_digram_service.generate_class_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

    activity_json = await activity_digram_service.generate_activity_json(
        formatted, usecase_json, class_json, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    puml_code = activity_digram_service.generate_activity_plantuml(activity_json)
    svg_url = utils.get_plantuml_svg(puml_code)

    return {"svg_url": svg_url, "plantuml_code": puml_code, "data": activity_json}


@router.get("/generate-sequence/{project_id}/{usecase_idx}")
async def generate_sequence(project_id: int, usecase_idx: int, db: Session = Depends(get_db)):
    formatted = _get_formatted_requirements(project_id, db)

    # Sequence diagram depends on Use Case + Class data
    usecase_json = await usecase_service.generate_usecase_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)
    class_json = await class_digram_service.generate_class_json(formatted, DEFAULT_PROVIDER, DEFAULT_MODEL)

    sequence_json = await sequence_digram_service.generate_sequence_json(
        usecase_idx, usecase_json, class_json, DEFAULT_PROVIDER, DEFAULT_MODEL
    )
    puml_code = sequence_digram_service.generate_sequence_plantuml(sequence_json, project_id, usecase_idx)
    svg_url = utils.get_plantuml_svg(puml_code)

    return {"svg_url": svg_url, "plantuml_code": puml_code, "data": sequence_json}