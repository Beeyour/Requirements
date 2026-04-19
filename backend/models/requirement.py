import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ReqType(str, enum.Enum):
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"

class ReqPriority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

# Software requirements management and versioning core.
class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False) # أضفنا Index

    type = Column(SQLEnum(ReqType), default=ReqType.FUNCTIONAL, nullable=False)
    priority = Column(SQLEnum(ReqPriority), default=ReqPriority.HIGH, nullable=False)

    description = Column(Text, nullable=False)

    version_number = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="requirements")
    logs = relationship("RequirementLog", back_populates="requirement", cascade="all, delete-orphan")

