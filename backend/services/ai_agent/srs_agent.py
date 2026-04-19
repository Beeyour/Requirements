
from typing import List, Dict, Any
from services.llm_client import call_llm, parse_json_response
from .prompts import _SRS_SYSTEM, _CONFLICT_SYSTEM

def generate_requirements_from_conversation(
    conversation_history: List[Dict[str, str]],
    app_name: str,
    provider: str,
    model: str,
) -> Dict[str, List[Dict]]:
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in conversation_history
    )
    raw = call_llm(
        provider, model,
        _SRS_SYSTEM,
        [{"role": "user", "content": f"Application: {app_name}\n\nTranscript:\n{transcript}"}],
        temperature=0.2,
        max_tokens=2500,
    )
    try:
        return parse_json_response(raw)
    except Exception:
        return {"functional": [], "non_functional": []}

def detect_conflicts(
    edited_requirement: Dict[str, Any],
    all_requirements: List[Dict[str, Any]],
    provider: str,
    model: str,
) -> Dict[str, Any]:
    others = [r for r in all_requirements if r["id"] != edited_requirement["id"]]
    if not others:
        return {"has_conflicts": False, "conflicts": []}

    others_text = "\n".join(
        f"[ID:{r['id']}] ({r['type']}) {r['description']}" for r in others
    )
    edited_text = (
        f"[ID:{edited_requirement['id']}] "
        f"({edited_requirement['type']}) {edited_requirement['description']}"
    )
    raw = call_llm(
        provider, model,
        _CONFLICT_SYSTEM,
        [{
            "role": "user",
            "content": f"EDITED REQUIREMENT:\n{edited_text}\n\nEXISTING REQUIREMENTS:\n{others_text}",
        }],
        temperature=0.1,
        max_tokens=1000,
    )
    try:
        return parse_json_response(raw)
    except Exception:
        return {"has_conflicts": False, "conflicts": []}