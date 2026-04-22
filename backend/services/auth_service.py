import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError 
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.auth import UserCreate

# --- Configuration ---
# Secret key should be stored in environment variables for production
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Security Utilities ---

def hash_password(password: str) -> str:
    # Generates a secure hash from a plain text password
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compares a plain password with a stored hash
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    # Generates a JWT access token with an expiration timestamp
    to_encode = data.copy()

    # Use timezone-aware UTC for global synchronization between server and client
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    # Decodes and validates the JWT; returns None if invalid or expired
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError: 
        # Correctly catches token tampering, expiration, or invalid format
        return None


# --- Database Operations ---

def get_user_by_email(db: Session, email: str):
    # Queries the database for a user matching the provided email
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate):
    # Hashes password and persists a new user record in the database
    hashed_pw = hash_password(user_data.password)

    # Manual mapping from Schema to SQLAlchemy Model to ensure data integrity
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user