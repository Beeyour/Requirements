import json
from sqlalchemy.orm import Session
from backend.services.uml.prompts import _SEQUENCE_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_sequence_plantuml, get_plantuml_svg
from backend.services.uml.persistence import get_ssot_context, get_latest_diagram_record, save_diagram
from backend.services.uml import usecase_service, class_digram_service
from backend.services.llm import call_llm
from backend.models.uml.sequence_diagram import SequenceDiagram
from backend.models.uml.usecase_diagram import UseCaseDiagram
from backend.schemas.uml.sequence import SequenceDiagramJSON


async def generate_sequence_json(
    usecase_idx: int,
    usecase_data: dict,
    class_data: dict,
    provider: str,
    model: str,
) -> dict:
    """Call LLM and return validated SequenceDiagramJSON dict for a specific use case.

    Injects full SSoT JSON into the prompt with strict vocabulary constraints.
    """
    use_cases = usecase_data.get("use_cases", [])
    actors = usecase_data.get("actors", [])
    classes = class_data.get("classes", [])

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

    # Full JSON context injection with strict instruction
    ssot_context = (
        "### SINGLE SOURCE OF TRUTH (SSoT) CONTEXT:\n"
        "You MUST strictly use ONLY the exact Classes, Actors, and Methods defined below.\n"
        "DO NOT invent, assume, or hallucinate any new classes, participants, or messages.\n\n"
        f"### Use Case Diagram (SSoT):\n{json.dumps(usecase_data, indent=2)}\n\n"
        f"### Class Diagram (SSoT):\n{json.dumps(class_data, indent=2)}\n\n"
        f"### Target Use Case: {target_uc}\n"
        f"### Linked Actors: {linked_actors}"
    )

    user_content = (
        f"Generate a Sequence Diagram for the Use Case '{target_uc}'.\n\n"
        "STRICT RULES:\n"
        "1. Participants MUST be exact Classes/Actors from the SSoT above.\n"
        "2. Messages MUST use exact Method names from the Class Diagram methods.\n"
        "3. You are FORBIDDEN from inventing participants or methods not in the SSoT.\n\n"
        f"{ssot_context}"
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


async def generate_sequence(
    db: Session,
    project_id: int,
    usecase_idx: int,
    formatted_requirements: str,
    provider: str,
    model: str,
) -> dict:
    """Generate Sequence diagram with SSoT from DB, save to DB, return standard response.

    If SSoT (UseCase + Class) doesn't exist in DB, generates and persists them first.
    Saves SequenceDiagram with usecase_id linkage.

    Returns:
        {"svg_url": str, "plantuml_code": str, "data": dict}
    """
    # Query SSoT from DB
    usecase_data, class_data = get_ssot_context(db, project_id)

    # If SSoT missing, generate and persist them first
    if usecase_data is None:
        result = await usecase_service.generate_usecase(
            db, project_id, formatted_requirements, provider, model
        )
        usecase_data = result["data"]

    if class_data is None:
        result = await class_digram_service.generate_class(
            db, project_id, formatted_requirements, provider, model
        )
        class_data = result["data"]

    # Validate usecase_idx after ensuring we have data
    use_cases = usecase_data.get("use_cases", [])
    if not (0 <= usecase_idx < len(use_cases)):
        raise ValueError(f"Use case index {usecase_idx} is out of range.")

    # Find the UseCaseDiagram record for linking
    usecase_record = get_latest_diagram_record(db, UseCaseDiagram, project_id)
    usecase_id = usecase_record.id if usecase_record else None

    # Generate Sequence with SSoT context
    data = await generate_sequence_json(usecase_idx, usecase_data, class_data, provider, model)
    plantuml_code = generate_sequence_plantuml(data, project_id, usecase_idx)
    svg_url = get_plantuml_svg(plantuml_code)

    save_diagram(
        db=db,
        model_class=SequenceDiagram,
        project_id=project_id,
        svg_url=svg_url,
        plantuml_code=plantuml_code,
        data=data,
        usecase_id=usecase_id,
    )

    return {"svg_url": svg_url, "plantuml_code": plantuml_code, "data": data}
