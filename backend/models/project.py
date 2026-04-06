from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from services.llm_client import DEFAULT_PROVIDER, DEFAULT_MODEL


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # LLM configuration — stored per project so each project can use a different model
    model_provider = Column(String(50), default=DEFAULT_PROVIDER, nullable=False)
    model_name = Column(String(100), default=DEFAULT_MODEL, nullable=False)

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
