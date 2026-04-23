from backend.database import Base
from backend.models.uml.mixin import UmlMixin


class ActivityDiagram(UmlMixin, Base):
    __tablename__ = "activity_diagrams"
