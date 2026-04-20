from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Request Schemas

class ProjectCreate(BaseModel):
    # Data required to initialize a new project
    app_name: str
    model_provider: str = "openai"
    model_name: str = "gpt-4o"


class ProjectModelUpdate(BaseModel):
    # Schema for updating the AI engine configuration
    model_provider: str
    model_name: str


# Response Schemas

class ProjectResponse(BaseModel):
    # Main response schema
    # All datetime fields are automatically ISO 8601 compliant
    id: int
    app_name: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    
    # This field is required here so the Router can inject it manually
    requirement_count: int

    # Allows Pydantic to validate SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)