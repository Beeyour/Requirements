from pydantic import BaseModel, Field
from typing import List, Literal, Union


class ParticipantInfo(BaseModel):
    name: str
    type: Literal["actor", "participant", "database", "boundary"]


class SequenceMessage(BaseModel):
    type: Literal["message"] = "message"
    from_idx: int
    to_idx: int
    is_return: bool = False
    text: str


class SequenceFragment(BaseModel):
    type: Literal["fragment"] = "fragment"
    fragment_type: Literal["alt", "opt", "loop"]
    condition: str
    steps: List["SequenceStep"] = Field(default_factory=list)


SequenceStep = Union[SequenceMessage, SequenceFragment]

# Update forward refs after Union definition
SequenceFragment.model_rebuild()


class SequenceDiagramJSON(BaseModel):
    title: str
    participants: List[ParticipantInfo]
    sequence: List[SequenceStep] = Field(default_factory=list)
