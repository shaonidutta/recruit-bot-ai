"""
Authentication Routes
Converted from backend/src/routes/authRoutes.js and backend/src/controllers/authController.js
User registration, login, token refresh, and profile management
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..models.user import UserCreate, UserInDB
from ..services.auth_service import AuthService
from ..auth.dependencies import get_current_user
from ..utils.response_helper import send_success, send_error

logger = logging.getLogger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refreshToken: str

@router.post("/register")
async def register(user_data: UserCreate):
    """
    Register a new user
    POST /api/v1/auth/register
    """
    try:
        result = await AuthService.register_user(user_data)
        return send_success(
            data=result,
            message="User registered successfully",
            status_code=201
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        send_error("Registration failed", 500)

@router.post("/login")
async def login(login_data: LoginRequest):
    """
    Login user with email and password
    POST /api/v1/auth/login
    """
    try:
        result = await AuthService.login_user(login_data.email, login_data.password)
        return send_success(
            data=result,
            message="Login successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        return send_error(f"Login failed: {str(e)}", 500)

@router.post("/refresh")
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    POST /api/v1/auth/refresh
    """
    try:
        logger.info("Attempting to refresh token")
        result = await AuthService.refresh_tokens(refresh_data.refreshToken)
        logger.info("Token refreshed successfully")
        return send_success(
            data=result,
            message="Token refreshed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        return send_error(f"Token refresh failed: {str(e)}", 500)

@router.get("/profile")
async def get_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user profile
    GET /api/v1/auth/profile
    """
    try:
        logger.info(f"Getting profile for user: {current_user.email}")
        result = await AuthService.get_user_profile(str(current_user.id))
        logger.info(f"Profile retrieved successfully for user: {current_user.email}")
        return send_success(
            data=result,
            message="Profile retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile for user {current_user.email}: {str(e)}", exc_info=True)
        return send_error(f"Failed to get profile: {str(e)}", 500)

@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    """
    Logout user (client-side token removal)
    POST /api/v1/auth/logout
    """
    try:
        # In a stateless JWT system, logout is handled client-side
        # This endpoint exists for consistency and future token blacklisting
        return send_success(
            data={"message": "Logged out successfully"},
            message="Logout successful"
        )
    except Exception as e:
        send_error("Logout failed", 500)
