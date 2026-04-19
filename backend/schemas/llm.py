from pydantic import BaseModel
from typing import Dict, List

class ModelInfoResponse(BaseModel):
    providers: Dict[str, List[str]]
    provider_labels: Dict[str, str]
    default_provider: str
    default_model: str