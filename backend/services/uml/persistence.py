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

def get_cached_diagram(db: Session, model_class: Type, project_id: int, **filters) -> Optional[dict]:
    """Return the standard API response dict if a diagram is cached, else None.
    Checks the latest diagram record matching the filters. If found, returns
    {"svg_url": ..., "plantuml_code": ..., "data": ...} directly.
    Args:
        db: SQLAlchemy session
        model_class: Diagram model class
        project_id: Project ID
        **filters: Extra filters (e.g., usecase_id for SequenceDiagram)
    Returns:
        The cached response dict or None
    """
    query = db.query(model_class).filter_by(project_id=project_id)
    for key, value in filters.items():
        query = query.filter(getattr(model_class, key) == value)
    record = query.order_by(model_class.created_at.desc()).first()
    if record and record.svg_url and record.parsed_data:
        return {
            "svg_url": record.svg_url,
            "plantuml_code": record.plantuml_code,
            "data": record.parsed_data,
        }
    return None

def get_latest_sequence_by_usecase_idx(
    db: Session, project_id: int, usecase_idx: int
) -> Optional[dict]:
    """Return cached sequence diagram for a specific use case index.
    Directly filters by project_id and usecase_idx for unique identification.
    Returns:
        The cached response dict or None
    """
    return get_cached_diagram(db, SequenceDiagram, project_id, usecase_idx=usecase_idx)

def get_all_sequence_diagrams(db: Session, project_id: int) -> list:
    """Return all sequence diagrams for a project, ordered by usecase_idx.
    Args:
        db: SQLAlchemy session
        project_id: Project ID
    Returns:
        List of SequenceDiagram ORM records
    """
    return (
        db.query(SequenceDiagram)
        .filter_by(project_id=project_id)
        .order_by(SequenceDiagram.usecase_idx.asc())
        .all()
    )
