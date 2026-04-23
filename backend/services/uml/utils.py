from plantuml import PlantUML
from pydantic import BaseModel, ValidationError
from backend.services.llm.utils import parse_json_response


# ---------------------------------------------------------------------------
# SVG rendering
# ---------------------------------------------------------------------------

def get_plantuml_svg(text: str) -> str:
    puml = PlantUML(url='https://www.plantuml.com/plantuml/svg/')
    try:
        return puml.get_url(text)
    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# JSON validation helper
# ---------------------------------------------------------------------------

def validate_and_parse_json(raw: str, schema_class: type[BaseModel]) -> dict:
    """Parse raw LLM output, validate against a Pydantic schema, return dict."""
    try:
        parsed = parse_json_response(raw)
    except Exception as e:
        raise ValueError(f"Failed to parse LLM JSON: {e}") from e

    try:
        model = schema_class.model_validate(parsed)
        return model.model_dump()
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}") from e


# ---------------------------------------------------------------------------
# PlantUML builders (deterministic, with bounds-checking)
# ---------------------------------------------------------------------------

def build_usecase_plantuml(data: dict, project_id: int) -> str:
    """Build a Use Case PlantUML string with interactive hyperlinks per use case."""
    actors = data.get("actors", [])
    use_cases = data.get("use_cases", [])
    system_title = data.get("system_title", "System")

    lines = [
        "@startuml",
        "left to right direction",
        "skinparam packageStyle rectangle",
        "skinparam shadowing false",
        "skinparam monochrome true",
        "",
    ]

    for i, name in enumerate(actors):
        lines.append(f'actor "{name}" as A{i}')

    lines.append(f'\nrectangle "{system_title}" {{')

    for i, name in enumerate(use_cases):
        link = f"/uml/generate_sequence/{project_id}/{i}"
        lines.append(f'    usecase "{name}" as UC{i} [[{link}]]')

    # includes
    for rel in data.get("includes", []):
        base = rel.get("base_idx") if isinstance(rel, dict) else rel[0]
        inc = rel.get("included_idx") if isinstance(rel, dict) else rel[1]
        if 0 <= base < len(use_cases) and 0 <= inc < len(use_cases):
            lines.append(f"    UC{base} ..> UC{inc} : <<include>>")

    # extends
    for rel in data.get("extends", []):
        ext = rel.get("extending_idx") if isinstance(rel, dict) else rel[0]
        base = rel.get("base_idx") if isinstance(rel, dict) else rel[1]
        if 0 <= ext < len(use_cases) and 0 <= base < len(use_cases):
            lines.append(f"    UC{ext} ..> UC{base} : <<extend>>")

    lines.append("}\n")

    # links (actor → use case)
    for rel in data.get("links", []):
        a_idx = rel.get("actor_idx") if isinstance(rel, dict) else rel[0]
        uc_idx = rel.get("usecase_idx") if isinstance(rel, dict) else rel[1]
        if 0 <= a_idx < len(actors) and 0 <= uc_idx < len(use_cases):
            lines.append(f"A{a_idx} --> UC{uc_idx}")

    lines.append("\n@enduml")
    return "\n".join(lines)


def build_class_plantuml(data: dict) -> str:
    """Build a Class Diagram PlantUML string."""
    classes = data.get("classes", [])

    lines = [
        "@startuml",
        "skinparam shadowing false",
        "skinparam monochrome true",
        "skinparam classAttributeIconSize 0",
        "left to right direction",
        "hide circle",
        "",
    ]

    for i, cls in enumerate(classes):
        name = cls.get("name", f"Class{i}")
        lines.append(f'class "{name}" as C{i} {{')
        for attr in cls.get("attributes", []):
            lines.append(f"    {attr}")
        for method in cls.get("methods", []):
            lines.append(f"    {method}")
        lines.append("}")
        lines.append("")

    mapping = {
        "inheritance": "<|--",
        "composition": "*--",
        "aggregation": "o--",
        "association": "--",
    }

    for rel in data.get("relationships", []):
        f_idx = rel.get("from_idx")
        t_idx = rel.get("to_idx")
        r_type = rel.get("type", "association")
        label = rel.get("label", "")

        if f_idx is None or t_idx is None:
            continue
        if not (0 <= f_idx < len(classes) and 0 <= t_idx < len(classes)):
            continue

        symbol = mapping.get(r_type, "--")
        desc = f" : {label}" if label else ""
        lines.append(f"C{f_idx} {symbol} C{t_idx}{desc}")

    lines.append("\n@enduml")
    return "\n".join(lines)


def build_activity_plantuml(data: dict) -> str:
    """Build an Activity Diagram PlantUML string with swimlanes using graph traversal."""
    swimlanes = data.get("swimlanes", [])
    nodes = data.get("nodes", [])
    transitions = data.get("transitions", [])
    title = data.get("title", "Activity")

    # Build adjacency list: from_idx -> [(to_idx, condition)]
    adj: dict[int, list[tuple[int, str]]] = {}
    for t in transitions:
        f = t.get("from_idx", -1)
        to = t.get("to_idx", -1)
        cond = t.get("condition", "")
        if 0 <= f < len(nodes) and 0 <= to < len(nodes):
            adj.setdefault(f, []).append((to, cond))

    # Track visited nodes to avoid infinite loops
    visited: set[int] = set()

    def _swimlane(idx: int) -> str:
        sl_idx = nodes[idx].get("swimlane_idx", 0) if 0 <= idx < len(nodes) else 0
        if 0 <= sl_idx < len(swimlanes):
            return f"|{swimlanes[sl_idx]}|"
        return ""

    def _walk(idx: int, out: list[str]) -> None:
        if idx in visited or not (0 <= idx < len(nodes)):
            return
        visited.add(idx)

        node = nodes[idx]
        n_type = node.get("type", "action")
        label = node.get("label", "")

        sl = _swimlane(idx)
        if sl:
            out.append(sl)

        if n_type == "start":
            out.append("start")
        elif n_type == "end":
            out.append("end")
            return
        elif n_type == "action":
            out.append(f":{label};")
        elif n_type == "decision":
            branches = adj.get(idx, [])
            if len(branches) >= 2:
                # First branch = "then" (condition from transition)
                out.append(f"if ({label}) then")
                to0, cond0 = branches[0]
                if cond0:
                    out.append(f"  ({cond0})")
                _walk(to0, out)

                out.append("else")
                to1, cond1 = branches[1]
                if cond1:
                    out.append(f"  ({cond1})")
                _walk(to1, out)

                # Additional branches become "elseif"
                for to_n, cond_n in branches[2:]:
                    out.append(f"elseif ({cond_n}) then")
                    _walk(to_n, out)

                out.append("endif")
            elif len(branches) == 1:
                out.append(f"if ({label}) then")
                _walk(branches[0][0], out)
                out.append("endif")
            else:
                out.append(f"if ({label}) then")
                out.append("endif")
        elif n_type == "fork":
            branches = adj.get(idx, [])
            for i, (to_n, _) in enumerate(branches):
                if i > 0:
                    out.append("fork again")
                else:
                    out.append("fork")
                _walk(to_n, out)
            out.append("end fork")
        elif n_type == "join":
            out.append("end fork")

        # Follow the default next transition for linear nodes (start, action)
        if n_type in ("start", "action"):
            nexts = adj.get(idx, [])
            if nexts:
                _walk(nexts[0][0], out)

    # Find start node
    start_idx = 0
    for i, node in enumerate(nodes):
        if node.get("type") == "start":
            start_idx = i
            break

    lines = [
        "@startuml",
        "skinparam shadowing false",
        "skinparam monochrome true",
        "",
        f"title {title}",
        "",
    ]

    if swimlanes:
        lines.append("|Swimlane|")
        for sl in swimlanes:
            lines.append(f"|{sl}|")

    _walk(start_idx, lines)

    lines.append("\n@enduml")
    return "\n".join(lines)


def _render_sequence_steps(steps: list, participant_count: int, indent: str = "    ") -> list:
    """Recursively render sequence steps (messages + fragments) into PlantUML lines."""
    lines = []
    for step in steps:
        step_type = step.get("type", "message")

        if step_type == "message":
            f_idx = step.get("from_idx", -1)
            t_idx = step.get("to_idx", -1)
            text = step.get("text", "")
            is_return = step.get("is_return", False)

            if not (0 <= f_idx < participant_count and 0 <= t_idx < participant_count):
                continue

            arrow = "-->" if is_return else "->"
            lines.append(f"{indent}P{f_idx} {arrow} P{t_idx} : {text}")

        elif step_type == "fragment":
            frag_type = step.get("fragment_type", "opt")
            condition = step.get("condition", "")
            inner_steps = step.get("steps", [])

            if frag_type == "alt":
                lines.append(f"{indent}alt {condition}")
            elif frag_type == "opt":
                lines.append(f"{indent}opt {condition}")
            elif frag_type == "loop":
                lines.append(f"{indent}loop {condition}")

            lines.extend(_render_sequence_steps(inner_steps, participant_count, indent + "    "))
            lines.append(f"{indent}end")

    return lines


def build_sequence_plantuml(data: dict, project_id: int, usecase_idx: int) -> str:
    """Build a Sequence Diagram PlantUML string with a return link to the Use Case diagram."""
    participants = data.get("participants", [])
    sequence = data.get("sequence", [])
    title = data.get("title", "Sequence")

    lines = [
        "@startuml",
        "skinparam shadowing false",
        "skinparam monochrome true",
        "",
        f"title {title}",
        "",
    ]

    # Participants
    type_map = {
        "actor": "actor",
        "participant": "participant",
        "database": "database",
        "boundary": "boundary",
    }

    for i, p in enumerate(participants):
        name = p.get("name", f"P{i}")
        p_type = type_map.get(p.get("type", "participant"), "participant")
        lines.append(f'{p_type} "{name}" as P{i}')

    lines.append("")

    # Sequence steps
    lines.extend(_render_sequence_steps(sequence, len(participants)))

    # Return link note
    back_link = f"/uml/generate-usecase/{project_id}"
    lines.append("")
    lines.append(f'hnote over P0 [[{back_link}]] : << Back to Use Case Diagram')

    lines.append("\n@enduml")
    return "\n".join(lines)
