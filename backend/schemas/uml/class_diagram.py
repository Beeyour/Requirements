from pydantic import BaseModel, Field
from typing import List, Literal

class ClassInfo(BaseModel):
    name: str
    attributes: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)

class ClassRelationship(BaseModel):
    from_idx: int
    to_idx: int
    type: Literal["inheritance", "composition", "aggregation", "association"]
    label: str = ""

class ClassDiagramJSON(BaseModel):
    system_title: str
    classes: List[ClassInfo]
    relationships: List[ClassRelationship] = Field(default_factory=list)
