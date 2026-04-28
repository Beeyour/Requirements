import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.uml.class_diagram import ClassDiagram
from backend.models.uml.sequence_diagram import SequenceDiagram
from backend.models.uml.usecase_diagram import UseCaseDiagram
from backend.services.uml.activity_digram_service import generate_activity
from backend.services.uml.sequence_digram_service import generate_sequence
from backend.services.uml.persistence import save_diagram


def _session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.mark.asyncio
async def test_activity_uses_persisted_ssot_without_regenerating(monkeypatch):
    db = _session()
    try:
        save_diagram(
            db=db,
            model_class=UseCaseDiagram,
            project_id=15,
            svg_url="u.svg",
            plantuml_code="@startuml\n@enduml",
            data={
                "system_title": "Clinic",
                "actors": ["Receptionist"],
                "use_cases": ["Register Patient"],
                "links": [{"actor_idx": 0, "usecase_idx": 0}],
                "includes": [],
                "extends": [],
            },
        )
        save_diagram(
            db=db,
            model_class=ClassDiagram,
            project_id=15,
            svg_url="c.svg",
            plantuml_code="@startuml\n@enduml",
            data={"system_title": "Clinic", "classes": [], "relationships": []},
        )
        async def fake_llm(*args, **kwargs):
            return (
                '{"title":"Register Patient Flow","swimlanes":["Receptionist"],'
                '"nodes":[{"id":"n0","type":"start","label":"","swimlane_idx":0},'
                '{"id":"n1","type":"end","label":"","swimlane_idx":0}],'
                '"transitions":[{"from_idx":0,"to_idx":1,"condition":""}]}'
            )
        async def _should_not_be_called(*args, **kwargs):
            raise AssertionError("Prerequisite SSoT generation should not run when DB context exists.")
        monkeypatch.setattr("backend.services.uml.activity_digram_service.call_llm", fake_llm)
        monkeypatch.setattr("backend.services.uml.activity_digram_service.get_plantuml_svg", lambda _: "a.svg")
        monkeypatch.setattr("backend.services.uml.activity_digram_service.usecase_service.generate_usecase", _should_not_be_called)
        monkeypatch.setattr("backend.services.uml.activity_digram_service.class_digram_service.generate_class", _should_not_be_called)
        result = await generate_activity(
            db=db,
            project_id=15,
            formatted_requirements="1. Register patient",
            provider="provider",
            model="model",
        )
        assert result["svg_url"] == "a.svg"
    finally:
        db.close()


@pytest.mark.asyncio
async def test_sequence_persists_with_latest_usecase_link(monkeypatch):
    db = _session()
    try:
        first = save_diagram(
            db=db,
            model_class=UseCaseDiagram,
            project_id=21,
            svg_url="u1.svg",
            plantuml_code="@startuml\n@enduml",
            data={
                "system_title": "Clinic",
                "actors": ["Receptionist"],
                "use_cases": ["Register Patient"],
                "links": [{"actor_idx": 0, "usecase_idx": 0}],
                "includes": [],
                "extends": [],
            },
        )
        latest = save_diagram(
            db=db,
            model_class=UseCaseDiagram,
            project_id=21,
            svg_url="u2.svg",
            plantuml_code="@startuml\n@enduml",
            data={
                "system_title": "Clinic",
                "actors": ["Receptionist"],
                "use_cases": ["Register Patient"],
                "links": [{"actor_idx": 0, "usecase_idx": 0}],
                "includes": [],
                "extends": [],
            },
        )
        assert latest.id > first.id
        save_diagram(
            db=db,
            model_class=ClassDiagram,
            project_id=21,
            svg_url="c.svg",
            plantuml_code="@startuml\n@enduml",
            data={
                "system_title": "Clinic",
                "classes": [{"name": "PatientService", "attributes": [], "methods": ["register()"]}],
                "relationships": [],
            },
        )
        async def fake_llm(*args, **kwargs):
            return (
                '{"title":"Register Patient","participants":[{"name":"Receptionist","type":"actor"},'
                '{"name":"PatientService","type":"participant"}],'
                '"sequence":[{"type":"message","from_idx":0,"to_idx":1,"is_return":false,"text":"register()"}]}'
            )
        monkeypatch.setattr("backend.services.uml.sequence_digram_service.call_llm", fake_llm)
        monkeypatch.setattr("backend.services.uml.sequence_digram_service.get_plantuml_svg", lambda _: "s.svg")
        result = await generate_sequence(
            db=db,
            project_id=21,
            usecase_idx=0,
            formatted_requirements="1. Register patient",
            provider="provider",
            model="model",
        )
        assert result["svg_url"] == "s.svg"
        rows = db.query(SequenceDiagram).filter_by(project_id=21).all()
        assert len(rows) == 1
        assert rows[0].usecase_id == latest.id
    finally:
        db.close()
