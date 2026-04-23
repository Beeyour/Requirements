import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.uml.class_diagram import ClassDiagram
from backend.services.uml.class_digram_service import generate_class, generate_class_json, generate_class_plantuml


@pytest.mark.asyncio
async def test_generate_class_digram_prompt_structure(monkeypatch):
    async def fake_llm(*args, **kwargs):
        return (
            '{"system_title":"Clinic","classes":[{"name":"Patient","attributes":[],"methods":[]}],'
            '"relationships":[]}'
        )

    monkeypatch.setattr("backend.services.uml.class_digram_service.call_llm", fake_llm)

    sample_req = "The user logs in."
    data = await generate_class_json(sample_req, "openai", "gpt-4o")
    prompt = generate_class_plantuml(data)

    assert "@startuml" in prompt
    assert "@enduml" in prompt
    assert "left to right direction" in prompt


@pytest.mark.asyncio
async def test_generate_class_digram_prompt_empty_error():
    with pytest.raises(ValueError):
        await generate_class_json("", "openai", "gpt-4o")


@pytest.mark.asyncio
async def test_generate_class_persists(monkeypatch):
    async def fake_llm(*args, **kwargs):
        return (
            '{"system_title":"Clinic","classes":[{"name":"Patient","attributes":[],"methods":[]}],'
            '"relationships":[]}'
        )

    monkeypatch.setattr("backend.services.uml.class_digram_service.call_llm", fake_llm)
    monkeypatch.setattr(
        "backend.services.uml.class_digram_service.get_plantuml_svg",
        lambda _: "https://example.com/class.svg",
    )

    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        result = await generate_class(
            db=db,
            project_id=7,
            formatted_requirements="1. Register patient",
            provider="provider",
            model="model",
        )
        assert result["svg_url"] == "https://example.com/class.svg"
        rows = db.query(ClassDiagram).filter_by(project_id=7).all()
        assert len(rows) == 1
        assert rows[0].parsed_data["classes"][0]["name"] == "Patient"
    finally:
        db.close()

