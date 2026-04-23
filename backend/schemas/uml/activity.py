from pydantic import BaseModel, Field
from typing import List, Literal


class ActivityNode(BaseModel):
    id: str
    type: Literal["start", "action", "decision", "fork", "join", "end"]
    label: str = ""
    swimlane_idx: int


class ActivityTransition(BaseModel):
    from_idx: int
    to_idx: int
    condition: str = ""


class ActivityDiagramJSON(BaseModel):
    title: str
    swimlanes: List[str]
    nodes: List[ActivityNode]
    transitions: List[ActivityTransition] = Field(default_factory=list)
