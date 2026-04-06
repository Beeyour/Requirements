from typing import List, Dict, Any
from services.llm_client import call_llm, parse_json_response

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_INTERVIEW_SYSTEM = """You are an expert Software Requirements Analyst conducting a structured \
interview to gather requirements for a software project.

Rules:
- Ask exactly ONE focused question per turn.
- Build on previous answers; never repeat a covered topic.
- Cover these areas in order: core purpose, target users, key features, user roles & permissions, \
data management, third-party integrations, performance & scalability, security & compliance, \
UI/UX expectations, technical constraints.
- Keep the tone professional yet conversational.
- After each answer give a brief acknowledgement before the next question.

When you have gathered sufficient information (typically 8-12 substantive exchanges), append the \
exact token SATURATION_DETECTED on its own line at the very end — do not explain it."""

_SATURATION_SYSTEM = """Analyse the conversation below and decide whether sufficient information \
exists to write a comprehensive Software Requirements Specification.

Return ONLY valid JSON — no markdown fences, no extra text:
{
  "is_saturated": <bool>,
  "coverage_percentage": <0-100>,
  "missing_areas": ["<area>", ...]
}"""

_SRS_SYSTEM = """You are a Software Requirements Analyst. Extract and formalise all requirements \
from the interview transcript below.

Return ONLY valid JSON — no markdown fences, no extra text:
{
  "functional": [{"description": "The system shall ..."}],
  "non_functional": [{"description": "The system shall ..."}]
}

Guidelines:
- Write every requirement as "The system shall …".
- Be specific and measurable where possible.
- Produce at least 6 functional and 4 non-functional requirements.
- No duplicates."""

_CONFLICT_SYSTEM = """You are a requirements consistency reviewer.

Determine whether the edited requirement below contradicts, duplicates, or creates an \
inconsistency with any of the existing requirements.

Return ONLY valid JSON — no markdown fences, no extra text:
{
  "has_conflicts": <bool>,
  "conflicts": [
    {
      "requirement_id": <int>,
      "description": "<brief label of the conflicting requirement>",
      "conflict_type": "contradiction|overlap|inconsistency",
      "explanation": "<detailed explanation>"
    }
  ]
}"""

# ---------------------------------------------------------------------------
# Public helpers — every function accepts provider + model
# ---------------------------------------------------------------------------

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
