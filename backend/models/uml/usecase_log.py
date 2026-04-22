from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class UseCaseLogs(Base):
    __tablename__ = "usecase_logs"
    id = Column(Integer, primary_key=True, index=True)
    usecase_id = Column(Integer, ForeignKey("usecases.id"), index=True, nullable=False)
    old_plantuml_code = Column(Text, nullable=True)
    version_number = Column(Integer, nullable=False)
    timestamp = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    usecase = relationship("UseCase", back_populates="logs")