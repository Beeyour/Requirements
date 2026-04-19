from database import Base # Import the shared Base
from .user import User
from .project import Project
from .requirement import Requirement
from .requirement_log import RequirementLog
from .conversation import ConversationHistory

# Ensure all models are linked to the Base metadata
__all__ = ["Base", "User", "Project", "Requirement", "RequirementLog", "ConversationHistory"]