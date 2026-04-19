from pydantic import BaseModel
from typing import List
from datetime import datetime

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    project_id: int
    content: str

class ChatResponse(BaseModel):
    message: str
    is_saturated: bool
    message_id: int
    history: List[MessageResponse]

class ResetRequest(BaseModel):
    project_id: int