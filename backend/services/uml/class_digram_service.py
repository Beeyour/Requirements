from typing import List
from backend.enums import ReqType
from backend.services.uml.prompts import _CLASS_DIAGRAM_SYSTEM
from backend.services.llm import call_llm
from backend.models import Requirement



async def generate_class_json(formatted_requirements: str, provider: str, model: str) -> str:
    if not formatted_requirements:
        raise ValueError("No requirements provided.")
    user_content = f"Analyze these requirements and extract entities for a Class Diagram:\n{formatted_requirements}"
    plantuml_json = await call_llm(
        provider, model,
        _CLASS_DIAGRAM_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        temperature=0.1,
        max_tokens= 1500,
        is_json=True
    )
    return plantuml_json.strip()

def generate_class_plantuml(data):
    lines = [
        "@startuml",
        "skinparam shadowing false",
        "skinparam monochrome true",
        "skinparam classAttributeIconSize 0", 
        "left to right direction",
        "hide circle",
        ""
    ]


    for i, cls in enumerate(data.get("classes", [])):
        class_name = cls.get("name", f"Class{i}")
        lines.append(f'class "{class_name}" as C{i} {{')

        for attr in cls.get("attributes", []):
            lines.append(f'    {attr}')

        for method in cls.get("methods", []):
            lines.append(f'    {method}')
        lines.append("}")
        lines.append("")


    for rel in data.get("relationships", []):
        f_idx = rel.get("from_idx")
        t_idx = rel.get("to_idx")
        r_type = rel.get("type", "association")
        label = rel.get("label", "")


        mapping = {
            "inheritance": "<|--",
            "composition": "*--",
            "aggregation": "o--",
            "association": "--"
        }
        symbol = mapping.get(r_type, "--")

        desc = f" : {label}" if label else ""

        lines.append(f"C{f_idx} {symbol} C{t_idx}{desc}")
    lines.append("\n@enduml")
    return "\n".join(lines)