
from typing import List, Dict, Any
from services.llm_client import call_llm, parse_json_response
from .prompts import _INTERVIEW_SYSTEM, _SATURATION_SYSTEM

def get_initial_greeting(app_name: str, provider: str, model: str) -> str:
    raw = call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        [{"role": "user", "content": f"I want to build a software application called '{app_name}'. Please start the requirements interview."}],
        temperature=0.7,
        max_tokens=400,
    )
    return raw.replace("SATURATION_DETECTED", "").strip()

def get_interview_response(
    conversation_history: List[Dict[str, str]],
    app_name: str,
    provider: str,
    model: str,
) -> Dict[str, Any]:
    raw = call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        list(conversation_history),
        temperature=0.7,
        max_tokens=500,
    )
    is_saturated = "SATURATION_DETECTED" in raw
    return {"message": raw.replace("SATURATION_DETECTED", "").strip(), "is_saturated": is_saturated}

def check_saturation(
    conversation_history: List[Dict[str, str]],
    provider: str,
    model: str,
) -> Dict[str, Any]:
    import json
    raw = call_llm(
        provider, model,
        _SATURATION_SYSTEM,
        [{"role": "user", "content": f"Conversation:\n{json.dumps(conversation_history, indent=2)}"}],
        temperature=0.1,
        max_tokens=250,
    )
    try:
        return parse_json_response(raw)
    except Exception:
        return {"is_saturated": False, "coverage_percentage": 0, "missing_areas": []}