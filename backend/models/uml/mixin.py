from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from datetime import datetime, timezone
from backend.database import Base


class UmlMixin:
    id = Column(Integer, primary_key=True, index=True)
    @declared_attr
    def project_id(cls):
        return Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    plantuml_code = Column(Text, nullable=True)
    svg_url = Column(String, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    @declared_attr
    def project(cls):
        return relationship("Project", back_populates=cls.__tablename__)
