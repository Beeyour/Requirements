from backend.services.llm.config import (
    AVAILABLE_MODELS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    PROVIDER_LABELS
)

def get_models_metadata():
    # Central service to fetch LLM metadata for the frontend
    # Returning the dictionary directly; Pydantic will validate it against the schema
    return {
        "providers": AVAILABLE_MODELS,
        "provider_labels": PROVIDER_LABELS,
        "default_provider": DEFAULT_PROVIDER,
        "default_model": DEFAULT_MODEL,
    }