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
