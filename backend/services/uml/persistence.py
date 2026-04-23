"""Persistence helpers for UML diagrams — Single Source of Truth (SSoT)."""
from typing import Type, Any, Optional
from sqlalchemy.orm import Session
from backend.models.uml.usecase_diagram import UseCaseDiagram
from backend.models.uml.class_diagram import ClassDiagram
from backend.models.uml.activity_diagram import ActivityDiagram
from backend.models.uml.sequence_diagram import SequenceDiagram


def save_diagram(
    db: Session,
    model_class: Type,
    project_id: int,
    svg_url: str,
    plantuml_code: str,
    data: dict,
    **kwargs
) -> Any:
    """Create and commit a diagram record, return the ORM instance.

    Args:
        db: SQLAlchemy session
        model_class: One of UseCaseDiagram, ClassDiagram, ActivityDiagram, SequenceDiagram
        project_id: Foreign key to projects.id
        svg_url: Remote PlantUML SVG URL
        plantuml_code: Raw PlantUML source
        data: Parsed JSON structure (the "data" key from API response)
        **kwargs: Extra columns (e.g., usecase_id for SequenceDiagram)

    Returns:
        The committed ORM instance
    """
    record = model_class(
        project_id=project_id,
        svg_url=svg_url,
        plantuml_code=plantuml_code,
        parsed_data=data,
        **kwargs,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_diagram(db: Session, model_class: Type, project_id: int) -> Optional[dict]:
    """Retrieve the most recent diagram's parsed_data for a project.

    Args:
        db: SQLAlchemy session
        model_class: Diagram model class
        project_id: Project ID

    Returns:
        The parsed_data dict or None if no record exists
    """
    record = (
        db.query(model_class)
        .filter_by(project_id=project_id)
        .order_by(model_class.created_at.desc())
        .first()
    )
    return record.parsed_data if record else None


def get_latest_diagram_record(db: Session, model_class: Type, project_id: int) -> Optional[Any]:
    """Retrieve the most recent diagram ORM record for a project."""
    return (
        db.query(model_class)
        .filter_by(project_id=project_id)
        .order_by(model_class.created_at.desc())
        .first()
    )


def get_ssot_context(db: Session, project_id: int) -> tuple[Optional[dict], Optional[dict]]:
    """Fetch UseCase and Class diagram data from DB (SSoT).

    Args:
        db: SQLAlchemy session
        project_id: Project ID

    Returns:
        (usecase_data, class_data) tuple — each may be None if not yet generated
    """
    usecase_data = get_latest_diagram(db, UseCaseDiagram, project_id)
    class_data = get_latest_diagram(db, ClassDiagram, project_id)
    return usecase_data, class_data
