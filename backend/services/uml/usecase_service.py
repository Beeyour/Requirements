from typing import List
from backend.enums import ReqType
from backend.services.uml.prompts import _UML_GENERATOR_SYSTEM
from backend.services.llm import call_llm
from backend.models import Requirement

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



async def generate_usecase_json(formatted_requirements: str, provider: str, model: str) -> str:
    if not formatted_requirements:
        raise ValueError("No requirements provided to generate UML.")

    user_content = f"Generate a Use Case diagram for these requirements:\n{formatted_requirements}"
    plantuml_json = await call_llm(
        provider, model,
        _UML_GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens=1000,
    )
    print(plantuml_json)
    return plantuml_json.strip()




def generate_plantuml(data):
    lines = [
        "@startuml",
        "left to right direction",
        "skinparam packageStyle rectangle",
        "skinparam shadowing false",
        "skinparam monochrome true",
        ""
    ]
    for i, actor_name in enumerate(data.get("actors", [])):
        lines.append(f'actor "{actor_name}" as A{i}')
    lines.append(f'\nrectangle "{data.get("system_title", "System")}" {{')
    for i, uc in enumerate(data.get("use_cases", [])):
        lines.append(f'    usecase "{uc}" as UC{i}')
    for base, inc in data.get("includes", []):
        lines.append(f"    UC{base} ..> UC{inc} : <<include>>")
    for ext, base in data.get("extends", []):
        lines.append(f"    UC{ext} ..> UC{base} : <<extend>>")
    lines.append("}\n")
    for a_idx, uc_idx in data.get("links", []):
        lines.append(f"A{a_idx} --> UC{uc_idx}")
    lines.append("\n@enduml")
    return "\n".join(lines)







