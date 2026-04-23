"""Quick smoke tests for PlantUML builders."""
from backend.services.uml.utils import (
    build_usecase_plantuml,
    build_class_plantuml,
    build_activity_plantuml,
    build_sequence_plantuml,
)


def test_usecase():
    data = {
        "system_title": "Clinic System",
        "actors": ["Receptionist", "Doctor"],
        "use_cases": ["Register Patient", "Book Consultation", "Generate Report"],
        "links": [
            {"actor_idx": 0, "usecase_idx": 0},
            {"actor_idx": 0, "usecase_idx": 1},
            {"actor_idx": 1, "usecase_idx": 2},
        ],
        "includes": [{"base_idx": 1, "included_idx": 0}],
        "extends": [],
    }
    puml = build_usecase_plantuml(data, 1)
    print("=== USE CASE ===")
    print(puml)
    assert "[[/uml/generate_sequence/1/0]]" in puml
    assert "A0 --> UC0" in puml
    assert "UC1 ..> UC0 : <<include>>" in puml
    print("Use Case: PASS\n")


def test_class():
    data = {
        "system_title": "Clinic System",
        "classes": [
            {
                "name": "Patient",
                "attributes": ["-name: String", "-dob: Date"],
                "methods": ["+getAge(): int"],
            },
            {
                "name": "Appointment",
                "attributes": ["-date: Date"],
                "methods": ["+schedule(): void"],
            },
        ],
        "relationships": [
            {"from_idx": 0, "to_idx": 1, "type": "composition", "label": "1 to *"}
        ],
    }
    puml = build_class_plantuml(data)
    print("=== CLASS ===")
    print(puml)
    assert "C0 *-- C1" in puml
    assert "Patient" in puml
    print("Class: PASS\n")


def test_activity():
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
        ],
    }
    puml = build_activity_plantuml(data)
    print("=== ACTIVITY ===")
    print(puml)
    assert "if (Is Valid?) then" in puml
    assert "Register Patient" in puml
    print("Activity: PASS\n")


def test_sequence():
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
    print("=== SEQUENCE ===")
    print(puml)
    assert "P0 -> P1 : enterDetails()" in puml
    assert "P2 --> P0 : confirmation" in puml
    assert "alt if valid" in puml
    assert "[[/uml/generate-usecase/1]]" in puml
    print("Sequence: PASS\n")


def test_bounds_checking():
    """Out-of-bounds indices should be silently skipped."""
    uc_data = {
        "system_title": "Test",
        "actors": ["A"],
        "use_cases": ["UC0"],
        "links": [{"actor_idx": 5, "usecase_idx": 99}],
        "includes": [{"base_idx": 10, "included_idx": 20}],
        "extends": [],
    }
    puml = build_usecase_plantuml(uc_data, 1)
    assert "A5" not in puml
    assert "UC99" not in puml
    print("Bounds checking: PASS\n")

    cls_data = {
        "system_title": "Test",
        "classes": [{"name": "C0", "attributes": [], "methods": []}],
        "relationships": [{"from_idx": 5, "to_idx": 10, "type": "association", "label": ""}],
    }
    puml = build_class_plantuml(cls_data)
    assert "C5" not in puml
    print("Class bounds checking: PASS\n")


if __name__ == "__main__":
    test_usecase()
    test_class()
    test_activity()
    test_sequence()
    test_bounds_checking()
    print("=== ALL TESTS PASSED ===")
