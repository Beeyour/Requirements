from typing import List
from backend.enums import ReqType
from backend.services.uml.prompts import _CLASS_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_class_plantuml
from backend.services.llm import call_llm
from backend.models import Requirement
from backend.schemas.uml.class_diagram import ClassDiagramJSON


async def generate_class_json(formatted_requirements: str, provider: str, model: str) -> dict:
    """Call LLM and return validated ClassDiagramJSON dict."""
    if not formatted_requirements:
        raise ValueError("No requirements provided.")

    user_content = f"Analyze these requirements and extract entities for a Class Diagram:\n{formatted_requirements}"
    raw = await call_llm(
        provider, model,
        _CLASS_DIAGRAM_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens=1500,
        is_json=True
    )
    return validate_and_parse_json(raw.strip(), ClassDiagramJSON)


def generate_class_plantuml(data: dict) -> str:
    """Build PlantUML string from validated class diagram data."""
    return build_class_plantuml(data)