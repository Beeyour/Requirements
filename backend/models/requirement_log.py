from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class RequirementLog(Base):
    __tablename__ = "requirement_logs"
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), index=True, nullable=False)
    old_description = Column(Text, nullable=True)
    change_reason = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    requirement = relationship("Requirement", back_populates="logs")
