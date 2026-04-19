from .llm_client import AVAILABLE_MODELS, DEFAULT_PROVIDER, DEFAULT_MODEL, PROVIDER_LABELS

def get_models_metadata():
    """Returns available LLM providers and models configuration."""
    return {
        "providers": AVAILABLE_MODELS,
        "provider_labels": PROVIDER_LABELS,
        "default_provider": DEFAULT_PROVIDER,
        "default_model": DEFAULT_MODEL,
    }