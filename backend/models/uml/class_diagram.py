from backend.database import Base
from backend.models.uml.mixin import UmlMixin


class ClassDiagram(UmlMixin, Base):
    __tablename__ = "class_diagrams"
