from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None