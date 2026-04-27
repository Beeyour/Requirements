import json
import logging
import re
from sqlalchemy.orm import Session
from backend.services.uml.prompts import _ACTIVITY_DIAGRAM_SYSTEM
from backend.services.uml.utils import validate_and_parse_json, build_activity_plantuml, get_plantuml_svg
from backend.services.uml.persistence import get_ssot_context, save_diagram
from backend.services.uml import usecase_service, class_digram_service
from backend.services.llm import call_llm
from backend.models.uml.activity_diagram import ActivityDiagram
from backend.schemas.uml.activity import ActivityDiagramJSON


def validate_plantuml_syntax(plantuml_code: str) -> str:
    """Validate and auto-fix common PlantUML syntax issues in activity diagrams.
    
    Uses count-based balancing with auto-correction instead of raising errors.
    Unmatched closing blocks are removed; missing closing blocks are appended.
    All fixes are logged for visibility in server logs.
    
    Args:
        plantuml_code: Raw PlantUML code string
        
    Returns:
        Fixed PlantUML code string (never raises)
    """
    logger = logging.getLogger(__name__)

    if not plantuml_code:
        logger.warning("PlantUML validation: empty code string, returning minimal diagram")
        return "@startuml\nstop\n@enduml"
    
    # Ensure proper start/end tags
    if not plantuml_code.strip().startswith('@startuml'):
        plantuml_code = '@startuml\n' + plantuml_code
        logger.info("PlantUML validation: added missing @startuml tag")
    if not plantuml_code.strip().endswith('@enduml'):
        plantuml_code = plantuml_code.rstrip() + '\n@enduml'
        logger.info("PlantUML validation: added missing @enduml tag")

    # --- Line-by-line count-based balancing with auto-correction ---
    lines = plantuml_code.split('\n')
    fixed_lines = []
    fork_counter = 0
    if_counter = 0

    for line in lines:
        stripped = line.strip()

        if stripped == 'fork':
            fork_counter += 1
            fixed_lines.append(line)
        elif stripped == 'fork again':
            # fork again continues the current fork block, doesn't change counter
            fixed_lines.append(line)
        elif stripped == 'end fork':
            if fork_counter > 0:
                fork_counter -= 1
                fixed_lines.append(line)
            else:
                # Unmatched end fork — remove it instead of crashing
                logger.warning(
                    "PlantUML validation: removed unmatched 'end fork' line: %s", line
                )
        elif stripped.startswith('if ') and '(' in stripped:
            if_counter += 1
            fixed_lines.append(line)
        elif stripped == 'endif':
            if if_counter > 0:
                if_counter -= 1
                fixed_lines.append(line)
            else:
                # Unmatched endif — remove it instead of crashing
                logger.warning(
                    "PlantUML validation: removed unmatched 'endif' line: %s", line
                )
        else:
            fixed_lines.append(line)

    # Auto-correct: append missing end fork statements before @enduml
    if fork_counter > 0:
        logger.warning(
            "PlantUML validation: appending %d missing 'end fork' statement(s)",
            fork_counter,
        )
        # Insert before the @enduml line
        enduml_idx = len(fixed_lines) - 1  # last line should be @enduml
        for _ in range(fork_counter):
            fixed_lines.insert(enduml_idx, 'end fork')

    # Auto-correct: append missing endif statements before @enduml
    if if_counter > 0:
        logger.warning(
            "PlantUML validation: appending %d missing 'endif' statement(s)",
            if_counter,
        )
        enduml_idx = len(fixed_lines) - 1
        for _ in range(if_counter):
            fixed_lines.insert(enduml_idx, 'endif')

    return '\n'.join(fixed_lines)


async def generate_activity_json(
    formatted_requirements: str,
    usecase_data: dict,
    class_data: dict,
    provider: str,
    model: str,
) -> dict:
    """Call LLM and return validated ActivityDiagramJSON dict.

    Injects full SSoT JSON into the prompt with strict vocabulary constraints.
    """
    if not formatted_requirements:
        raise ValueError("No requirements provided to generate Activity Diagram.")

    # Full JSON context injection with strict instruction
    ssot_context = (
        "### SINGLE SOURCE OF TRUTH (SSoT) CONTEXT:\n"
        "You MUST strictly use ONLY the exact Actors, Classes, and Use Cases defined below.\n"
        "DO NOT invent, assume, or hallucinate any new entities, swimlanes, or actions.\n\n"
        f"### Use Case Diagram (SSoT):\n{json.dumps(usecase_data, indent=2)}\n\n"
        f"### Class Diagram (SSoT):\n{json.dumps(class_data, indent=2)}\n\n"
        f"### SRS Requirements:\n{formatted_requirements}"
    )

    user_content = (
        "Generate an Activity Diagram for these requirements.\n\n"
        "STRICT RULES:\n"
        "1. Swimlanes MUST be exact Actor/Class names from the SSoT above.\n"
        "2. Action labels MUST reuse exact Use Case names from SSoT where applicable.\n"
        "3. You are FORBIDDEN from inventing new entities not in the SSoT.\n\n"
        f"{ssot_context}"
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
    """Build PlantUML string from validated activity diagram data with syntax validation."""
    plantuml_code = build_activity_plantuml(data)
    # Validate and fix syntax issues
    return validate_plantuml_syntax(plantuml_code)


async def generate_activity(
    db: Session,
    project_id: int,
    formatted_requirements: str,
    provider: str,
    model: str,
) -> dict:
    """Generate Activity diagram with SSoT from DB, save to DB, return standard response.

    If SSoT (UseCase + Class) doesn't exist in DB, generates and persists them first.

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

    # Generate Activity with SSoT context
    data = await generate_activity_json(formatted_requirements, usecase_data, class_data, provider, model)
    plantuml_code = generate_activity_plantuml(data)
    svg_url = get_plantuml_svg(plantuml_code)

    save_diagram(
        db=db,
        model_class=ActivityDiagram,
        project_id=project_id,
        svg_url=svg_url,
        plantuml_code=plantuml_code,
        data=data,
    )

    return {"svg_url": svg_url, "plantuml_code": plantuml_code, "data": data}
