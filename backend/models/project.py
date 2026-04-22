from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

# Default LLM configurations
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-4o"

class Project(Base):
    # Central entity representing a software requirement project.
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    app_name = Column(String(255), nullable=False)
    
    # LLM Settings: Allows flexibility to switch between providers (OpenAI, Google, etc.)
    model_provider = Column(String(50), default=DEFAULT_PROVIDER, nullable=False)
    model_name = Column(String(100), default=DEFAULT_MODEL, nullable=False)

    # Time-aware UTC timestamps for global client synchronization
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Database Relationships
    # Using string-based references to avoid circular import issues
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
