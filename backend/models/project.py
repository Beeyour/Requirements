from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o"

# Central project container and LLM configuration settings.
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    model_provider = Column(String(50), default=DEFAULT_PROVIDER, nullable=False)
    model_name = Column(String(100), default=DEFAULT_MODEL, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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