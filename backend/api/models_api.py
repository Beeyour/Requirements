<<<<<<< HEAD
from fastapi import APIRouter
from backend.schemas.llm import ModelInfoResponse
from backend.services import llm_service

router = APIRouter()

@router.get("/models", response_model=ModelInfoResponse)
def get_available_models():
    # API Endpoint to retrieve AI configuration for frontend dropdowns
    return llm_service.get_models_metadata()
=======
from fastapi import APIRouter
from services.llm_client import AVAILABLE_MODELS, DEFAULT_PROVIDER, DEFAULT_MODEL, PROVIDER_LABELS

router = APIRouter()


@router.get("/models")
def get_available_models():
    return {
        "providers": AVAILABLE_MODELS,
        "provider_labels": PROVIDER_LABELS,
        "default_provider": DEFAULT_PROVIDER,
        "default_model": DEFAULT_MODEL,
    }
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
