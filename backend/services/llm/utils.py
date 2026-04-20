import json
import re
from typing import Any
from backend.services.llm.config import AVAILABLE_MODELS

def parse_json_response(text: str) -> Any:
    """Strip optional markdown fences then parse JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "",  cleaned.strip(), flags=re.MULTILINE)
    return json.loads(cleaned.strip())



def validate_model(provider: str, model: str) -> None:
    if provider not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown provider '{provider}'")
    if model not in AVAILABLE_MODELS[provider]:
        raise ValueError(f"Unknown model '{model}' for provider '{provider}'")

