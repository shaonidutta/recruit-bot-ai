"""
JWT Utility Functions
Converted from backend/src/utils/jwt.js
Handles token generation, verification, and management
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
import bcrypt

# Password hashing using bcrypt directly

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "your-refresh-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))

def generate_access_token(payload: Dict[str, Any]) -> str:
    """Generate JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode = payload.copy()
    to_encode.update({
        "exp": expire,
        "iss": "ai-recruitment-agent",
        "aud": "ai-recruitment-users"
    })
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_refresh_token(payload: Dict[str, Any]) -> str:
    """Generate JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)
    to_encode = payload.copy()
    to_encode.update({
        "exp": expire,
        "iss": "ai-recruitment-agent",
        "aud": "ai-recruitment-users"
    })
    return jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)

def generate_tokens(user: Dict[str, Any]) -> Dict[str, str]:
    """Generate both access and refresh tokens"""
    access_payload = {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"]
    }
    
    refresh_payload = {
        "id": str(user["_id"])
    }
    
    return {
        "accessToken": generate_access_token(access_payload),
        "refreshToken": generate_refresh_token(refresh_payload)
    }

def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify and decode access token"""
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM],
            audience="ai-recruitment-users",
            issuer="ai-recruitment-agent"
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify and decode refresh token"""
    try:
        payload = jwt.decode(
            token, 
            JWT_REFRESH_SECRET, 
            algorithms=[JWT_ALGORITHM],
            audience="ai-recruitment-users",
            issuer="ai-recruitment-agent"
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid refresh token: {str(e)}")

def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """Extract token from Authorization header"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
