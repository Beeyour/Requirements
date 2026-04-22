<<<<<<< HEAD
import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
<<<<<<< HEAD
from datetime import datetime
from backend.database import Base
=======
from datetime import datetime, timezone
from database import Base
>>>>>>> 083f654 (try to solve the history time issue)

<<<<<<< HEAD
<<<<<<< HEAD
class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# Chat history and context management for AI interactions.
=======
#
>>>>>>> ac43216 (test)
=======

>>>>>>> 5ac59ce (synchronize the backend with main)
class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    role = Column(SQLEnum(ChatRole), default=ChatRole.USER, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )
    is_archived = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="conversations")
=======
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(50), nullable=False)       # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        )
    is_archived = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="conversations")
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
