from pydantic import BaseModel
from typing import List
from datetime import datetime
from services.llm_client import DEFAULT_PROVIDER, DEFAULT_MODEL

class ProjectCreate(BaseModel):
    app_name: str
    model_provider: str = DEFAULT_PROVIDER
    model_name: str = DEFAULT_MODEL

class ProjectModelUpdate(BaseModel):
    model_provider: str
    model_name: str

class ProjectResponse(BaseModel):
    id: int
    app_name: str
    created_at: datetime
    requirement_count: int
    model_provider: str
    model_name: str

    class Config:
        from_attributes = True # Allow Pydantic to read SQLAlchemy models