from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import UserCreate, Token
from services import auth_service

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Handles user registration and returns an access token."""
    # Check if user already exists
    if auth_service.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Save user to database
    user = auth_service.create_user(db, user_data)

    # Generate JWT
    token_data = {"sub": str(user.id), "email": user.email}
    token = auth_service.create_access_token(token_data)

    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user_id": user.id, 
        "email": user.email
    }

@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """Authenticates user and returns an access token."""
    # Find user and verify password
    user = auth_service.get_user_by_email(db, user_data.email)
    if not user or not auth_service.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT
    token_data = {"sub": str(user.id), "email": user.email}
    token = auth_service.create_access_token(token_data)

    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user_id": user.id, 
        "email": user.email
    }