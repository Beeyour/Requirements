from enum import Enum
# Re-defining Enums for validation consistency (matches your SQLAlchemy Enums)
class ReqType(str, Enum):
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"

class ReqPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"