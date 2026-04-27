import json
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
    """Validate and fix common PlantUML syntax issues in activity diagrams.
    
    Args:
        plantuml_code: Raw PlantUML code string
        
    Returns:
        Fixed PlantUML code string
        
    Raises:
        ValueError: If syntax cannot be automatically fixed
    """
    if not plantuml_code:
        raise ValueError("Empty PlantUML code")
    
    # Ensure proper start/end tags
    if not plantuml_code.strip().startswith('@startuml'):
        plantuml_code = '@startuml\n' + plantuml_code
    if not plantuml_code.strip().endswith('@enduml'):
        plantuml_code = plantuml_code.rstrip() + '\n@enduml'
    
    # Count fork and end fork blocks
    fork_count = len(re.findall(r'^\s*fork\s*$', plantuml_code, re.MULTILINE))
    end_fork_count = len(re.findall(r'^\s*end fork\s*$', plantuml_code, re.MULTILINE))
    
    # Count if and endif blocks
    if_count = len(re.findall(r'^\s*if\s*\(', plantuml_code, re.MULTILINE))
    endif_count = len(re.findall(r'^\s*endif\s*$', plantuml_code, re.MULTILINE))
    
    # Fix missing end fork blocks
    if fork_count > end_fork_count:
        missing_end_forks = fork_count - end_fork_count
        # Add missing end fork statements before @enduml
        end_fork_fix = '\n'.join(['end fork'] * missing_end_forks)
        plantuml_code = plantuml_code.replace('@enduml', f'{end_fork_fix}\n@enduml')
    
    # Fix missing endif blocks
    if if_count > endif_count:
        missing_endifs = if_count - endif_count
        # Add missing endif statements before @enduml
        endif_fix = '\n'.join(['endif'] * missing_endifs)
        plantuml_code = plantuml_code.replace('@enduml', f'{endif_fix}\n@enduml')
    
    # Validate swimlane declarations (should be at top after title)
    lines = plantuml_code.split('\n')
    swimlane_pattern = re.compile(r'^\|(\w+)\|$')
    swimlanes_found = []
    title_found = False
    swimlane_section_start = -1
    
    for i, line in enumerate(lines):
        if line.strip().startswith('title'):
            title_found = True
        elif swimlane_pattern.match(line.strip()):
            if swimlane_section_start == -1:
                swimlane_section_start = i
            swimlanes_found.append(swimlane_pattern.match(line.strip()).group(1))
    
    # Check for balanced fork/join in the actual structure
    # This is a more sophisticated check for nested structures
    fork_count = 0
    if_count = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped == 'fork':
            fork_count += 1
        elif stripped == 'fork again':
            # fork again continues the current fork block, doesn't change count
            continue
        elif stripped == 'end fork':
            fork_count -= 1
            if fork_count < 0:
                raise ValueError("Unmatched 'end fork' found - no corresponding fork")
        elif stripped.startswith('if ') and '(' in stripped:
            if_count += 1
        elif stripped == 'endif':
            if_count -= 1
            if if_count < 0:
                raise ValueError("Unmatched 'endif' found - no corresponding if")
    
    if fork_count > 0:
        raise ValueError(f"Missing {fork_count} 'end fork' statement(s)")
    elif if_count > 0:
        raise ValueError(f"Missing {if_count} 'endif' statement(s)")
    
    return plantuml_code


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
