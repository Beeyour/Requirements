import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.enums import ReqType, ReqPriority
from backend.models.uml.usecase_diagram import UseCaseDiagram
from backend.services.uml.usecase_service import (
    format_requirements_for_ai,
    generate_plantuml,
    generate_usecase,
    generate_usecase_json,
)

def test_format_requirements_logic():
    class MockRequirement:
        def __init__(self, description, req_type, is_active=True, priority=ReqPriority.HIGH):
            self.description = description
            self.type = req_type
            self.is_active = is_active
            self.priority = priority
    reqs = [
        MockRequirement("The user can login", ReqType.FUNCTIONAL),
        MockRequirement("The system should be fast", ReqType.NON_FUNCTIONAL),
        MockRequirement("Old requirement", ReqType.FUNCTIONAL, is_active=False)
    ]
    formatted_text = format_requirements_for_ai(reqs)
    assert "The user can login" in formatted_text
    assert "The system should be fast" not in formatted_text
    assert "Old requirement" not in formatted_text

@pytest.mark.asyncio
async def test_generate_usecase_prompt_structure(monkeypatch):
    async def fake_llm(*args, **kwargs):
        return (
            '{"system_title":"Clinic","actors":["Receptionist"],'
            '"use_cases":["Register Patient"],'
            '"links":[{"actor_idx":0,"usecase_idx":0}],'
            '"includes":[],"extends":[]}'
        )
    monkeypatch.setattr("backend.services.uml.usecase_service.call_llm", fake_llm)
    sample_req = "The user logs in."
    data = await generate_usecase_json(sample_req, "openai", "gpt-4o")
    prompt = generate_plantuml(data, project_id=1)
    assert "@startuml" in prompt
    assert "@enduml" in prompt
    assert "left to right direction" in prompt

@pytest.mark.asyncio
async def test_generate_usecase_prompt_empty_error():
    with pytest.raises(ValueError):
        await generate_usecase_json("", "openai", "gpt-4o")

@pytest.mark.asyncio
async def test_generate_usecase_persists(monkeypatch):
    async def fake_llm(*args, **kwargs):
        return (
            '{"system_title":"Clinic","actors":["Receptionist"],'
            '"use_cases":["Register Patient"],'
            '"links":[{"actor_idx":0,"usecase_idx":0}],'
            '"includes":[],"extends":[]}'
        )
    monkeypatch.setattr("backend.services.uml.usecase_service.call_llm", fake_llm)
    monkeypatch.setattr(
        "backend.services.uml.usecase_service.get_plantuml_svg",
        lambda _: "https://example.com/diagram.svg",
    )
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        result = await generate_usecase(
            db=db,
            project_id=99,
            formatted_requirements="1. Register patient",
            provider="provider",
            model="model",
        )
        assert result["svg_url"] == "https://example.com/diagram.svg"
        assert result["data"]["use_cases"] == ["Register Patient"]
        rows = db.query(UseCaseDiagram).filter_by(project_id=99).all()
        assert len(rows) == 1
        assert rows[0].parsed_data["system_title"] == "Clinic"
    finally:
        db.close()