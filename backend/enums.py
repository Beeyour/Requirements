from enum import Enum

class ReqType(str, Enum):
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"

class ReqPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"