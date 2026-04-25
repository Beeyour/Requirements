from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# ننشئ Config مشترك لتجنب التكرار (اختياري لكن أنظف)
shared_config = ConfigDict(protected_namespaces=())

# Request Schemas

class ProjectCreate(BaseModel):
    # أضفنا الإعداد هنا لأن الحقول تبدأ بـ model_
    model_config = shared_config
    
    app_name: str
    model_provider: str = "openai"
    model_name: str = "gpt-4o"


class ProjectModelUpdate(BaseModel):
    # وأيضاً هنا
    model_config = shared_config
    
    model_provider: str
    model_name: str


# Response Schemas

class ProjectResponse(BaseModel):
    id: int
    app_name: str
    model_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    requirement_count: int


    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=() 
    )