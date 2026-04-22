from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models import User
from backend.api.dependencies import get_current_user
from backend.schemas.uml.usecase import UseCaseResponse
from backend.services.uml import usecase_service

router = APIRouter()

@router.get("/generate-uml/{project_id}", response_model=UseCaseResponse)
async def get_uml(project_id: int, db: Session = Depends(get_db)):


    db_requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    clean_requirements = format_requirements_for_ai(db_requirements)
    
    final_prompt = generate_uml_prompt(clean_requirements, "use_case")
    
    # 4. إرسالها للذكاء الاصطناعي
    ai_response = call_llm_for_uml(final_prompt)
    

    
    return


@router.get("/generate-uml/{project_id}", response_model=UseCaseResponse)
async def generate_uml(project_id: int, db: Session = Depends(get_db)):

    return await usecase_service.generate_and_save_uml(project_id, db)
