from fastapi import APIRouter
from schemas.llm import ModelInfoResponse
from services import llm_service

router = APIRouter()

@router.get("/models", response_model=ModelInfoResponse)
def get_available_models():
    """Endpoint to retrieve available AI models and providers configuration."""
    return llm_service.get_models_metadata()
