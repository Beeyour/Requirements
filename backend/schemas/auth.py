from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

# Request Schemas

class UserCreate(BaseModel):
    # Schema for user registration
    email: EmailStr
    password: str
    full_name: str = "user"


class UserUpdate(BaseModel):
    # Schema for updating user profile. All fields are optional
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


# Response Schemas

class UserResponse(BaseModel):
    # Standard response schema
    # Pydantic serializes datetime to ISO 8601 by default
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Enable ORM compatibility to read from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    # Simplified schema for login only
    email: EmailStr
    password: str



# Authentication Schemas

class Token(BaseModel):
    # JWT Token response schema
    access_token: str
    token_type: str
    user_id: int
    email: str


class TokenData(BaseModel):
    # Schema for data embedded in the JWT token
    user_id: Optional[str] = None
    email: Optional[str] = None