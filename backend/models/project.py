from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    model_provider = Column(String(50), default=DEFAULT_PROVIDER, nullable=False)
    model_name = Column(String(100), default=DEFAULT_MODEL, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
    # string-based refs to dodge circular imports
    user = relationship("User", back_populates="projects")
    conversations = relationship(
        "ConversationHistory",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    requirements = relationship(
        "Requirement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    usecase_diagrams = relationship(
        "UseCaseDiagram",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    class_diagrams = relationship(
        "ClassDiagram",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    activity_diagrams = relationship(
        "ActivityDiagram",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    sequence_diagrams = relationship(
        "SequenceDiagram",
        back_populates="project",
        cascade="all, delete-orphan",
    )
