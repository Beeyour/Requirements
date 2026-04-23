from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


# --- UseCase Logs Schemas ---

class UseCaseLogResponse(BaseModel):
    id: int
    usecase_id: int
    old_plantuml_code: str
    version_number: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


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


# --- LLM Structured Output Schemas (Index-based) ---

class LinkRel(BaseModel):
    actor_idx: int
    usecase_idx: int

class IncludeRel(BaseModel):
    base_idx: int
    included_idx: int

class ExtendRel(BaseModel):
    extending_idx: int
    base_idx: int

class UseCaseJSON(BaseModel):
    system_title: str
    actors: List[str]
    use_cases: List[str]
    links: List[LinkRel] = Field(default_factory=list)
    includes: List[IncludeRel] = Field(default_factory=list)
    extends: List[ExtendRel] = Field(default_factory=list)
