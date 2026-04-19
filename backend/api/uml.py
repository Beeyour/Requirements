from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import User
from .dependencies import get_current_user
from schemas.uml import UMLResponse
from services import uml_service

router = APIRouter()

@router.post("/projects/{project_id}/generate-uml", response_model=UMLResponse)
def generate_uml(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Triggers the AI agent to create a UML diagram based on project requirements."""
    # Validate project ownership
    project = uml_service.get_project_or_404(db, project_id, current_user.id)
    
    # Generate UML content
    uml_code = uml_service.process_uml_generation(db, project)

    return UMLResponse(
        project_id=project_id,
        uml_output=uml_code,
        generated_at=datetime.utcnow(),
    )