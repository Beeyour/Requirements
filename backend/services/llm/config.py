# Model definitions and UI labels for 2026 standards

# Dictionary mapping provider keys to another dictionary of { model_id: display_name }
AVAILABLE_MODELS = {
    "openai": {
        "gpt-5.4-nano": "GPT 5.4",
    },
    "google": {
        "gemini-3.1-flash-lite-preview": "Gemini 3.1 Flash Lite",  
    },
    "anthropic": {
        "claude-3-5-sonnet-latest": "Claude 3.5 Sonnet",
        "claude-3-opus-latest": "Claude 3 Opus",
    },
}

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.4-nano"

PROVIDER_LABELS = {
    "openai": "OpenAI",
    "google": "Google Gemini",
    "anthropic": "Anthropic Claude",
}