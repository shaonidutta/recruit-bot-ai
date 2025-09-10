"""
Authentication Dependencies
Converted from backend/src/middleware/auth.js
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user import UserService, UserInDB
from .jwt_handler import verify_access_token

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    Get current authenticated user from JWT token
    Equivalent to auth middleware in Node.js
    """
    try:
        # Verify token
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = await UserService.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserInDB]:
    """
    Get current user if token is provided, otherwise return None
    For optional authentication
    """
    if not credentials:
        return None
    
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("id")
        
        if user_id:
            user = await UserService.find_by_id(user_id)
            return user
    except:
        pass
    
    return None

def require_auth(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Require authentication - raises 401 if not authenticated
    """
    return user
