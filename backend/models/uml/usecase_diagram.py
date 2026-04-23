from sqlalchemy.orm import relationship
from backend.database import Base
from backend.models.uml.mixin import UmlMixin


class UseCaseDiagram(UmlMixin, Base):
    __tablename__ = "usecase_diagrams"

    sequences = relationship(
        "SequenceDiagram",
        back_populates="usecase_diagram",
        cascade="all, delete-orphan",
    )
