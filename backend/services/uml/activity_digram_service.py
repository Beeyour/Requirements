from backend.services.uml.prompts import _ACTIVITY_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_activity_plantuml
from backend.services.llm import call_llm
from backend.schemas.uml.activity import ActivityDiagramJSON


async def generate_activity_json(
    formatted_requirements: str,
    usecase_data: dict,
    class_data: dict,
    provider: str,
    model: str,
) -> dict:
    """Call LLM and return validated ActivityDiagramJSON dict.

    The activity diagram is constrained to reuse actors/classes from the
    existing Use Case and Class diagrams.
    """
    if not formatted_requirements:
        raise ValueError("No requirements provided to generate Activity Diagram.")

    # Summarize existing diagram data for the LLM context
    actors = usecase_data.get("actors", [])
    use_cases = usecase_data.get("use_cases", [])
    classes = [c.get("name", "") for c in class_data.get("classes", [])]

    context = (
        f"### Existing Use Case Diagram Actors:\n{actors}\n\n"
        f"### Existing Use Cases:\n{use_cases}\n\n"
        f"### Existing Classes:\n{classes}\n\n"
        f"### SRS Requirements:\n{formatted_requirements}"
    )

    user_content = (
        "Generate an Activity Diagram for these requirements. "
        "Reuse the actors and classes listed above as swimlanes, "
        "and reuse use case names as action labels where applicable:\n"
        f"{context}"
    )

    raw = await call_llm(
        provider, model,
        _ACTIVITY_DIAGRAM_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens=2000,
        is_json=True,
    )
    return validate_and_parse_json(raw.strip(), ActivityDiagramJSON)


def generate_activity_plantuml(data: dict) -> str:
    """Build PlantUML string from validated activity diagram data."""
    return build_activity_plantuml(data)
