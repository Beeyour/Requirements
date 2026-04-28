from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Response Schemas
class MessageResponse(BaseModel):
    # Represents a single message in the conversation history
    # datetime type ensures automatic ISO 8601 serialization for frontend
    id: int
    role: str
    content: str
    timestamp: Optional[datetime] = None
    # Enables compatibility with SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    # Main response object after sending a message
    message: str
    is_saturated: bool
    message_id: int
    history: List[MessageResponse]
    # Enables compatibility with SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)

# Request Schemas
class ChatRequest(BaseModel):
    # Data required to send a new message
    project_id: int
    content: str

class ResetRequest(BaseModel):
    # Data required to reset the chat session
    project_id: int