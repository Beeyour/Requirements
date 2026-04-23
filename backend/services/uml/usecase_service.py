from typing import List
from backend.enums import ReqType
from backend.services.uml.prompts import _UML_GENERATOR_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_usecase_plantuml
from backend.services.llm import call_llm
from backend.models import Requirement
from backend.schemas.uml.usecase import UseCaseJSON


def format_requirements_for_ai(requirements: List[Requirement]) -> str:
    formatted_lines = ["### Project Functional Requirements List:"]
    counter = 1
    for req in requirements:
        if req.is_active and req.type == ReqType.FUNCTIONAL:
            line = f"{counter}. {req.description} [Priority: {req.priority.name}]"
            formatted_lines.append(line)
            counter += 1
    if counter == 1:
        return ""
    return "\n".join(formatted_lines)


async def generate_usecase_json(formatted_requirements: str, provider: str, model: str) -> dict:
    """Call LLM and return validated UseCaseJSON dict."""
    if not formatted_requirements:
        raise ValueError("No requirements provided to generate UML.")

    user_content = f"Generate a Use Case diagram for these requirements:\n{formatted_requirements}"
    raw = await call_llm(
        provider, model,
        _UML_GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens=1000,
        is_json=True
    )
    return validate_and_parse_json(raw.strip(), UseCaseJSON)


def generate_plantuml(data: dict, project_id: int) -> str:
    """Build PlantUML string from validated use case data with interactive hyperlinks."""
    return build_usecase_plantuml(data, project_id)









