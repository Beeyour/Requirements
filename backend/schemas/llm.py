from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class ModelInfoResponse(BaseModel):
    # This structure expects a list of strings for each provider
    providers: Dict[str, List[str]]
    provider_labels: Dict[str, str]
    default_provider: str
    default_model: str

    # Fix for Pydantic V2 protected namespaces warning ('model_')
    model_config = ConfigDict(protected_namespaces=())