from pydantic import BaseModel, Field
from typing import List

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
