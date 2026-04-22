from sqlalchemy import Column,JSON, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base
from backend.enums import ReqPriority


class UseCase(Base):
    __tablename__ = "usecases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    title = Column(String, nullable=True) 
    raw_json = Column(JSON, nullable=True) 
    plantuml_code = Column(Text, nullable=True) 
    version_number = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )


    project = relationship("Project", back_populates="usecases")
    logs = relationship("UseCaseLogs", back_populates="usecase", cascade="all, delete-orphan")




