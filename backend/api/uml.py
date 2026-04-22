from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models import User
from backend.api.dependencies import get_current_user
# from backend.schemas.uml.usecase import UseCaseResponse
from backend.services import requirement_service
from backend.services.uml import usecase_service
from backend.services.uml import utils




router = APIRouter()

@router.get("/generate-uml/{project_id}")
async def get_uml(project_id: int, db: Session = Depends(get_db)):

    requirements = requirement_service.get_project_requirements(db, project_id, False)

    ai_json = usecase_service.format_requirements_for_ai(requirements)

    usecase_json = await usecase_service.generate_usecase_json(ai_json)

    puml_code = usecase_service.generate_plantuml(usecase_json)


    svg_url = utils.get_plantuml_svg(puml_code)


    return {
        "svg_url": svg_url,
    }