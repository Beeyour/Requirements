from fastapi import APIRouter
from backend.schemas.llm import ModelInfoResponse
from backend.services import llm_service

router = APIRouter()

@router.get("/models", response_model=ModelInfoResponse)
def get_available_models():
    return llm_service.get_models_metadata()
