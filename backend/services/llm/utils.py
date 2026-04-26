import json
import re
from typing import Any
from backend.services.llm.config import AVAILABLE_MODELS

def parse_json_response(text: str, fallback: Any = None) -> Any:
    """Strip optional markdown fences then parse JSON with robust error handling."""
    if not text or not text.strip():
        return fallback or {}
    
    # Try to extract JSON from the text
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "",  cleaned.strip(), flags=re.MULTILINE)
    
    # Try to find JSON object in the text (handles cases where JSON is embedded)
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group()
    
    try:
        parsed = json.loads(cleaned.strip())
        # Ensure we return a dictionary
        if isinstance(parsed, dict):
            return parsed
        elif fallback is not None:
            return fallback
        else:
            return {"data": parsed}
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw text: {text[:200]}...")
        return fallback or {}
    except Exception as e:
        print(f"Unexpected error parsing JSON: {e}")
        return fallback or {}



def validate_model(provider: str, model: str) -> None:
    if provider not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown provider '{provider}'")
    if model not in AVAILABLE_MODELS[provider]:
        raise ValueError(f"Unknown model '{model}' for provider '{provider}'")

