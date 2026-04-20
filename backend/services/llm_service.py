from backend.services.llm.config import (
    AVAILABLE_MODELS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    PROVIDER_LABELS
)

def get_models_metadata():
    """
    Returns the full configuration metadata to the frontend.
    Now including nested dictionaries for providers to show display names.
    """
    return {
        # Directly returning the dictionary without using .keys() 
        # as we updated the schema to support Dict[str, str]
        "providers": AVAILABLE_MODELS, 
        "provider_labels": PROVIDER_LABELS,
        "default_provider": DEFAULT_PROVIDER,
        "default_model": DEFAULT_MODEL,
    }