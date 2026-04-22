from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
# Updated to absolute imports for consistency across the backend
from backend.database import get_db
from backend.models.user import User
from backend.services import auth_service

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    # FastAPI dependency to validate JWT and return the current user
    
    # 1. Decode the token using the auth_service (Synchronous)
    payload = auth_service.decode_access_token(credentials.credentials)
    
    if payload is None:
        # Standard 401 response for expired or invalid tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Extract user ID from payload (sub)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # 3. Verify user existence in DB (Synchronous query)
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    # Return the user object to be used in protected routes
    return user
