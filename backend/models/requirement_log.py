from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class RequirementLog(Base):
    __tablename__ = "requirement_logs"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=False)
    change_reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="logs")
