from typing import List
from sqlalchemy.orm import Session
from backend.enums import ReqType
from backend.services.uml.prompts import _CLASS_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_class_plantuml, get_plantuml_svg
from backend.services.uml.persistence import save_diagram
from backend.services.llm import call_llm
from backend.models import Requirement
from backend.models.uml.class_diagram import ClassDiagram
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


async def generate_class(
    db: Session,
    project_id: int,
    formatted_requirements: str,
    provider: str,
    model: str,
) -> dict:
    """Generate Class diagram, save to DB, return standard response.

    Returns:
        {"svg_url": str, "plantuml_code": str, "data": dict}
    """
    data = await generate_class_json(formatted_requirements, provider, model)
    plantuml_code = generate_class_plantuml(data)
    svg_url = get_plantuml_svg(plantuml_code)

    save_diagram(
        db=db,
        model_class=ClassDiagram,
        project_id=project_id,
        svg_url=svg_url,
        plantuml_code=plantuml_code,
        data=data,
    )

    return {"svg_url": svg_url, "plantuml_code": plantuml_code, "data": data}