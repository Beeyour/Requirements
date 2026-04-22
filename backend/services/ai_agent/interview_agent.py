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
        return {"is_saturated": False, "coverage_percentage": 0, "missing_areas": []}

async def get_initial_greeting(app_name: str, provider: str, model: str) -> str:
    # Triggers the first question of the interview
    raw = await call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        [{"role": "user", "content": f"I want to build a software application called '{app_name}'. Please start the requirements interview."}],
        temperature=0.7,
        max_tokens=400,
    )
    # Clean output from potential hidden saturation tags
    return raw.replace("SATURATION_DETECTED", "").strip()

async def get_interview_response(
    conversation_history: List[Dict[str, str]],
    app_name: str,
    provider: str,
    model: str,
) -> Dict[str, Any]:
    # Gets the next analyst question and checks for the saturation token
    raw = await call_llm(
        provider, model,
        _INTERVIEW_SYSTEM,
        list(conversation_history),
        temperature=0.7,
        max_tokens=500,
    )
    # The saturation token might be present in the text if specified in prompts.py
    is_saturated = "SATURATION_DETECTED" in raw
    return {
        "message": raw.replace("SATURATION_DETECTED", "").strip(), 
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
    )
    return parse_json_response(raw)