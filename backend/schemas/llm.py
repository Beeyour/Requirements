from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class ModelInfoResponse(BaseModel):
    # Change: From Dict[str, List[str]] to Dict[str, Dict[str, str]]
    # This allows the API to return both the Model ID and its Display Name
    providers: Dict[str, Dict[str, str]] 
    provider_labels: Dict[str, str]
    default_provider: str
    default_model: str
    # Standard config to handle Pydantic protected namespaces
    model_config = ConfigDict(protected_namespaces=())