from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime



# --- UseCase Main Schemas ---

class UseCaseBase(BaseModel):
    plantuml_code: str

class UseCaseCreate(UseCaseBase):
    project_id: int

class UseCaseUpdate(UseCaseBase):
    plantuml_code: str
    description: str

class UseCaseResponse(UseCaseBase):
    id: int
    project_id: int
    version_number: int
    created_at: datetime
    updated_at: datetime
    logs: List[UseCaseLogResponse] = []
    model_config = ConfigDict(from_attributes=True)

# --- UseCase Logs Schemas ---

class UseCaseLogResponse(BaseModel):
    id: int
    usecase_id: int
    old_plantuml_code: str
    version_number: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
