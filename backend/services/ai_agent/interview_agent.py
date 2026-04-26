import json
import re
from typing import List, Dict, Any

# Absolute imports from the centralized LLM package
from backend.services.llm import call_llm
from backend.services.ai_agent.prompts import _INTERVIEW_SYSTEM, _SATURATION_SYSTEM

def parse_json_response(raw_text: str) -> Dict[str, Any]:
    # Utility to clean LLM response and extract valid JSON
    # It handles cases where AI wraps JSON in ```json ... ``` blocks
    try:
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(raw_text)
    except (json.JSONDecodeError, AttributeError):
        return {
            "acknowledgment": "",
            "question": "",
            "is_saturated": False,
            "coverage_percentage": 0,
            "missing_areas": [],
        }


def _build_interview_message(parsed: Dict[str, Any]) -> str:
    """Build the display message from parsed JSON, with fallback."""
    ack = (parsed.get("acknowledgment") or "").strip()
    question = (parsed.get("question") or "").strip()
    if ack and question:
        return f"{ack}\n\n{question}"
    if ack or question:
        return ack or question
    # Both empty — return a safe fallback question
    return "Could you tell me more about what you'd like the system to do?"


DEFAULT_RETRY_QUESTION = (
    "I'd like to understand your project better. "
    "Could you describe the main purpose of the application and who will use it?"
)

async def get_initial_greeting(app_name: str, provider: str, model: str) -> str:
    # Triggers the first question of the interview
    raw = await call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        [{"role": "user", "content": f"I want to build a software application called '{app_name}'. Please start the requirements interview."}],
        temperature=0.7,
        max_tokens=400,
        is_json=True,
    )
    parsed = parse_json_response(raw)
    message = _build_interview_message(parsed)

    # Retry once if the message is the fallback (both ack and question were empty)
    if message == DEFAULT_RETRY_QUESTION:
        raw = await call_llm(
            provider, model,
            _INTERVIEW_SYSTEM,
            [{"role": "user", "content": f"I want to build a software application called '{app_name}'. Please start the requirements interview."}],
            temperature=0.5,
            max_tokens=400,
            is_json=True,
        )
        parsed = parse_json_response(raw)
        message = _build_interview_message(parsed)

    return message or "Let's start. What is the core purpose of your application?"

async def get_interview_response(
    conversation_history: List[Dict[str, str]],
    app_name: str,
    provider: str,
    model: str,
) -> Dict[str, Any]:
    # Gets the next analyst turn and parses strict JSON output
    raw = await call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        list(conversation_history),
        temperature=0.7,
        max_tokens=500,
        is_json=True,
    )
    parsed = parse_json_response(raw)
    message = _build_interview_message(parsed)

    # Retry once if both ack and question were empty
    if message == DEFAULT_RETRY_QUESTION:
        raw = await call_llm(
            provider, model,
            _INTERVIEW_SYSTEM,
            list(conversation_history),
            temperature=0.5,
            max_tokens=500,
            is_json=True,
        )
        parsed = parse_json_response(raw)
        message = _build_interview_message(parsed)

    is_saturated = bool(parsed.get("is_saturated", False))
    return {
        "message": message,
        "is_saturated": is_saturated
    }

async def check_saturation(
    conversation_history: List[Dict[str, str]],
    provider: str,
    model: str,
) -> Dict[str, Any]:
    # Forces the LLM to output a JSON status by evaluating context
    raw = await call_llm(
        provider, model,
        _SATURATION_SYSTEM,
        [{"role": "user", "content": f"Conversation history for evaluation:\n{json.dumps(conversation_history)}"}],
        temperature=0.1,
        max_tokens=300,
        is_json=True,
    )
    return parse_json_response(raw)