<<<<<<< HEAD
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
<<<<<<< HEAD
from backend.database import Base
=======
from database import Base
>>>>>>> 083f654 (try to solve the history time issue)

class ReqType(str, enum.Enum):
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"

class ReqPriority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Requirement(Base):
    # Handles individual software requirements, versioning, and status tracking
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    # Linked to project with index for optimized lookup
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)

    type = Column(SQLEnum(ReqType), default=ReqType.FUNCTIONAL, nullable=False)
    priority = Column(SQLEnum(ReqPriority), default=ReqPriority.HIGH, nullable=False)
    description = Column(Text, nullable=False)

    # Tracks requirement evolution through versions
    version_number = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
<<<<<<< HEAD

    # Global standard UTC timestamps for cross-client compatibility
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
=======
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )
>>>>>>> 083f654 (try to solve the history time issue)

    project = relationship("Project", back_populates="requirements")
    logs = relationship("RequirementLog", back_populates="requirement", cascade="all, delete-orphan")
=======
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    type = Column(String(50), nullable=False)         # "Functional" or "Non-Functional"
    description = Column(Text, nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )

    project = relationship("Project", back_populates="requirements")
    logs = relationship(
        "RequirementLog",
        back_populates="requirement",
        cascade="all, delete-orphan",
    )
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
