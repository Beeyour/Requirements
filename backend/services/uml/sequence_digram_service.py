from backend.services.uml.prompts import _SEQUENCE_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_sequence_plantuml
from backend.services.llm import call_llm
from backend.schemas.uml.sequence import SequenceDiagramJSON


async def generate_sequence_json(
    usecase_idx: int,
    usecase_data: dict,
    class_data: dict,
    provider: str,
    model: str,
) -> dict:
    """Call LLM and return validated SequenceDiagramJSON dict for a specific use case.

    Feeds the LLM the target use case details AND the class diagram metadata.
    """
    use_cases = usecase_data.get("use_cases", [])
    actors = usecase_data.get("actors", [])
    classes = [c.get("name", "") for c in class_data.get("classes", [])]

    if not (0 <= usecase_idx < len(use_cases)):
        raise ValueError(f"Use case index {usecase_idx} is out of range.")

    target_uc = use_cases[usecase_idx]

    # Find which actors are linked to this use case
    linked_actors = []
    for link in usecase_data.get("links", []):
        a_idx = link.get("actor_idx") if isinstance(link, dict) else link[0]
        uc_idx = link.get("usecase_idx") if isinstance(link, dict) else link[1]
        if uc_idx == usecase_idx and 0 <= a_idx < len(actors):
            linked_actors.append(actors[a_idx])

    context = (
        f"### Target Use Case: {target_uc}\n\n"
        f"### Actors linked to this use case: {linked_actors}\n\n"
        f"### Available Classes from Class Diagram:\n{classes}\n\n"
        f"### All Use Cases (for context):\n{use_cases}"
    )

    user_content = (
        f"Generate a Sequence Diagram for the Use Case '{target_uc}'. "
        "The first participant must be the Actor. "
        "Other participants should be Classes from the Class Diagram.\n"
        f"{context}"
    )

    raw = await call_llm(
        provider, model,
        _SEQUENCE_DIAGRAM_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens=1500,
        is_json=True,
    )
    return validate_and_parse_json(raw.strip(), SequenceDiagramJSON)


def generate_sequence_plantuml(data: dict, project_id: int, usecase_idx: int) -> str:
    """Build PlantUML string from validated sequence diagram data with return link."""
    return build_sequence_plantuml(data, project_id, usecase_idx)
