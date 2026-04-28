from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
from backend.enums import ReqType, ReqPriority

# Response Schemas
class RequirementLogResponse(BaseModel):
    # Schema for individual requirement change logs
    id: int
    requirement_id: int
    old_description: Optional[str] = None
    change_reason: Optional[str] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class RequirementResponse(BaseModel):
    # Standard response for a requirement
    # Pydantic serializes datetime to ISO 8601 automatically
    id: int
    project_id: int
    type: ReqType
    priority: ReqPriority
    description: str
    version_number: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UpdateRequirementResponse(BaseModel):
    # Specialized response for update operations, including AI feedback
    requirement: RequirementResponse
    conflict_report: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

# Request Schemas
class RequirementCreate(BaseModel):
    # Schema for creating a new requirement manually
    project_id: int
    description: str
    type: ReqType = ReqType.FUNCTIONAL
    priority: ReqPriority = ReqPriority.MEDIUM

class UpdateRequirementRequest(BaseModel):
    # Schema for modifying a requirement
    description: str
    # Reason for the modification, will be saved in RequirementLog
    change_reason: Optional[str] = None

class GenerateSRSRequest(BaseModel):
    # Request to trigger AI SRS generation for a project
    project_id: int