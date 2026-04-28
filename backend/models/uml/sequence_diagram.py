from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.uml.mixin import UmlMixin


class SequenceDiagram(UmlMixin, Base):
    __tablename__ = "sequence_diagrams"
    usecase_idx = Column(
        Integer,
        index=True,
        nullable=False,
        comment="Index of the use case in the use case diagram (0-based)"
    )
    usecase_id = Column(
        Integer,
        ForeignKey("usecase_diagrams.id"),
        index=True,
        nullable=True,
    )
    usecase_diagram = relationship(
        "UseCaseDiagram",
        back_populates="sequences",
    )
