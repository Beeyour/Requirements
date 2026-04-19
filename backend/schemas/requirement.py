from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class RequirementResponse(BaseModel):
    id: int
    project_id: int
    type: str
    description: str
    version_number: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GenerateSRSRequest(BaseModel):
    project_id: int

class UpdateRequirementRequest(BaseModel):
    description: str
    change_reason: Optional[str] = None

class UpdateRequirementResponse(BaseModel):
    requirement: RequirementResponse
    conflict_report: Optional[Dict[str, Any]] = None