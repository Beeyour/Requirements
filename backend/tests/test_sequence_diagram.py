"""Tests for Sequence Diagram and Activity Diagram PlantUML generation."""
from backend.services.uml.utils import (
    build_activity_plantuml,
    build_sequence_plantuml,
    build_usecase_plantuml,
)


def test_activity_diagram_with_decision():
    """Activity diagram with decision branches, swimlanes, and stop termination."""
    data = {
        "title": "Registration Process",
        "swimlanes": ["Receptionist", "System"],
        "nodes": [
            {"id": "n0", "type": "start", "label": "", "swimlane_idx": 0},
            {"id": "n1", "type": "action", "label": "Register Patient", "swimlane_idx": 0},
            {"id": "n2", "type": "decision", "label": "Is Valid?", "swimlane_idx": 1},
            {"id": "n3", "type": "action", "label": "Save Record", "swimlane_idx": 1},
            {"id": "n4", "type": "action", "label": "Show Error", "swimlane_idx": 0},
            {"id": "n5", "type": "end", "label": "", "swimlane_idx": 1},
        ],
        "transitions": [
            {"from_idx": 0, "to_idx": 1, "condition": ""},
            {"from_idx": 1, "to_idx": 2, "condition": ""},
            {"from_idx": 2, "to_idx": 3, "condition": "Yes"},
            {"from_idx": 2, "to_idx": 4, "condition": "No"},
            {"from_idx": 3, "to_idx": 5, "condition": ""},
            {"from_idx": 4, "to_idx": 5, "condition": ""},
        ],
    }
    puml = build_activity_plantuml(data)
    # Conditions on same line as if/else
    assert "if (Is Valid?) then (Yes)" in puml
    assert "else (No)" in puml
    # Use 'stop', never 'end' for termination
    assert "stop" in puml
    # No dummy |Swimlane| line
    assert "|Swimlane|" not in puml
    # Swimlanes declared at top
    assert "|Receptionist|" in puml
    assert "|System|" in puml
    print("Activity diagram: PASS")


def test_sequence_diagram_basic():
    """Sequence diagram with messages, return messages, and fragment."""
    data = {
        "title": "Register Patient",
        "participants": [
            {"name": "Receptionist", "type": "actor"},
            {"name": "Patient", "type": "participant"},
            {"name": "Database", "type": "database"},
        ],
        "sequence": [
            {"type": "message", "from_idx": 0, "to_idx": 1, "is_return": False, "text": "enterDetails()"},
            {"type": "message", "from_idx": 1, "to_idx": 2, "is_return": False, "text": "save()"},
            {"type": "message", "from_idx": 2, "to_idx": 0, "is_return": True, "text": "confirmation"},
            {
                "type": "fragment",
                "fragment_type": "alt",
                "condition": "if valid",
                "steps": [
                    {"type": "message", "from_idx": 2, "to_idx": 1, "is_return": True, "text": "success"}
                ],
            },
        ],
    }
    puml = build_sequence_plantuml(data, 1, 0)
    # Messages use correct arrow types
    assert "P0 -> P1 : enterDetails()" in puml
    assert "P2 --> P0 : confirmation" in puml
    # Fragment rendered correctly
    assert "alt if valid" in puml
    assert "end" in puml
    # Back link to use case diagram
    assert "[[/generate-usecase/1]]" in puml
    print("Sequence diagram: PASS")


def test_sequence_diagram_from_usecase_hyperlink():
    """Use case diagram hyperlinks point to the correct sequence endpoint."""
    data = {
        "system_title": "Clinic System",
        "actors": ["Receptionist"],
        "use_cases": ["Register Patient", "Book Consultation"],
        "links": [{"actor_idx": 0, "usecase_idx": 0}],
        "includes": [],
        "extends": [],
    }
    puml = build_usecase_plantuml(data, 5)
    # Each use case has a clickable hyperlink to its sequence diagram
    assert "[[/generate-sequence/5/0]]" in puml
    assert "[[/generate-sequence/5/1]]" in puml
    # Alias format: UC_{idx}
    assert "UC_0" in puml
    assert "UC_1" in puml
    print("Use Case hyperlink: PASS")


if __name__ == "__main__":
    test_activity_diagram_with_decision()
    test_sequence_diagram_basic()
    test_sequence_diagram_from_usecase_hyperlink()
    print("\n=== ALL SEQUENCE DIAGRAM TESTS PASSED ===")
