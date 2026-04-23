"""Quick smoke tests for Pydantic schema validation."""
from backend.services.uml.utils import validate_and_parse_json
from backend.schemas.uml.usecase import UseCaseJSON
from backend.schemas.uml.class_diagram import ClassDiagramJSON
from backend.schemas.uml.activity import ActivityDiagramJSON
from backend.schemas.uml.sequence import SequenceDiagramJSON


def test_usecase_validation():
    raw = '{"system_title": "Test", "actors": ["A"], "use_cases": ["UC0"], "links": [{"actor_idx": 0, "usecase_idx": 0}]}'
    result = validate_and_parse_json(raw, UseCaseJSON)
    assert result["actors"] == ["A"]
    print("UseCaseJSON validation: PASS")


def test_class_validation():
    raw = '{"system_title": "Test", "classes": [{"name": "C0", "attributes": ["-x: int"], "methods": ["+foo(): void"]}], "relationships": [{"from_idx": 0, "to_idx": 0, "type": "association", "label": "self"}]}'
    result = validate_and_parse_json(raw, ClassDiagramJSON)
    assert result["classes"][0]["name"] == "C0"
    print("ClassDiagramJSON validation: PASS")


def test_activity_validation():
    raw = '{"title": "Test", "swimlanes": ["SL0"], "nodes": [{"id": "n0", "type": "start", "label": "", "swimlane_idx": 0}], "transitions": [{"from_idx": 0, "to_idx": 0, "condition": ""}]}'
    result = validate_and_parse_json(raw, ActivityDiagramJSON)
    assert result["swimlanes"] == ["SL0"]
    print("ActivityDiagramJSON validation: PASS")


def test_sequence_validation():
    raw = '{"title": "Test", "participants": [{"name": "P0", "type": "actor"}], "sequence": [{"type": "message", "from_idx": 0, "to_idx": 0, "is_return": false, "text": "test()"}]}'
    result = validate_and_parse_json(raw, SequenceDiagramJSON)
    assert result["participants"][0]["name"] == "P0"
    print("SequenceDiagramJSON validation: PASS")


def test_invalid_json():
    try:
        validate_and_parse_json("not json", UseCaseJSON)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("Invalid JSON error handling: PASS")


if __name__ == "__main__":
    test_usecase_validation()
    test_class_validation()
    test_activity_validation()
    test_sequence_validation()
    test_invalid_json()
    print("=== ALL SCHEMA TESTS PASSED ===")
