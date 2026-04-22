from typing import List, Dict, Any

# Absolute imports from the centralized LLM package
from backend.services.llm import call_llm
from backend.services.ai_agent.prompts import _SRS_SYSTEM, _CONFLICT_SYSTEM
from backend.services.llm.utils import parse_json_response

async def generate_requirements_from_conversation(
    conversation_history: List[Dict[str, str]],
    app_name: str,
    provider: str,
    model: str,
) -> Dict[str, List[Dict]]:
    # Formats history into a transcript and extracts structured requirements
    
    # Building a readable transcript for the LLM analyst
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in conversation_history
    )
    
    # SRS generation requires low temperature for structural consistency
    raw = await call_llm(
        provider, model,
        _SRS_SYSTEM,
        [{"role": "user", "content": f"Application: {app_name}\n\nTranscript:\n{transcript}"}],
        temperature=0.2,
        max_tokens=2500,
    )
    
    parsed = parse_json_response(raw)
    
    # Ensure the structure matches the frontend expectation even on AI failure
    return {
        "functional": parsed.get("functional", []),
        "non_functional": parsed.get("non_functional", [])
    }

async def detect_conflicts(
    edited_requirement: Dict[str, Any],
    all_requirements: List[Dict[str, Any]],
    provider: str,
    model: str,
) -> Dict[str, Any]:
    # Compares an edited requirement against existing ones to ensure consistency
    
    # Filter out the requirement currently being edited
    others = [r for r in all_requirements if r.get("id") != edited_requirement.get("id")]
    
    if not others:
        return {"has_conflicts": False, "conflicts": []}

    # Formatting requirements list for the AI judge
    others_text = "\n".join(
        f"[ID:{r.get('id')}] ({r.get('type')}) {r.get('description')}" for r in others
    )
    edited_text = (
        f"[ID:{edited_requirement.get('id')}] "
        f"({edited_requirement.get('type')}) {edited_requirement.get('description')}"
    )
    
    # Highly deterministic temperature for logical conflict detection
    raw = await call_llm(
        provider, model,
        _CONFLICT_SYSTEM,
        [{
            "role": "user",
            "content": f"EDITED REQUIREMENT:\n{edited_text}\n\nEXISTING REQUIREMENTS:\n{others_text}",
        }],
        temperature=0.1,
        max_tokens=1000,
    )
    
    parsed = parse_json_response(raw)
    
    # Ensuring standard response format for the frontend
    return {
        "has_conflicts": parsed.get("has_conflicts", False),
        "conflicts": parsed.get("conflicts", [])
    }