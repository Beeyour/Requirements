from backend.services.llm.config import (
    AVAILABLE_MODELS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    PROVIDER_LABELS
)

def get_models_metadata():
    """
    Transforms the nested dictionary from config into a format 
    compatible with the Pydantic Response Schema.
    """
    # Transform Dict[str, Dict[str, str]] -> Dict[str, List[str]]
    # We extract only the IDs (keys) for the 'providers' field
    transformed_providers = {
        provider: list(models.keys()) 
        for provider, models in AVAILABLE_MODELS.items()
    }

    return {
        "providers": transformed_providers,
        "provider_labels": PROVIDER_LABELS,
        "default_provider": DEFAULT_PROVIDER,
        "default_model": DEFAULT_MODEL,
    }