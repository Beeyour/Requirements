from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base
from backend.enums import ReqType, ReqPriority


class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    type = Column(SQLEnum(ReqType), default=ReqType.FUNCTIONAL, nullable=False)
    priority = Column(SQLEnum(ReqPriority), default=ReqPriority.HIGH, nullable=False)
    description = Column(Text, nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
    project = relationship("Project", back_populates="requirements")
    logs = relationship("RequirementLog", back_populates="requirement", cascade="all, delete-orphan")