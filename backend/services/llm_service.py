from backend.services.llm.config import (
    AVAILABLE_MODELS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    PROVIDER_LABELS
)

def get_models_metadata():
    # We need to transform the dictionaries of models into lists of model IDs
    # to match the Pydantic schema (Dict[str, List[str]])
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