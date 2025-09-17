"""
Authentication Service
Converted from backend/src/services/authService.js
Handles user registration, login, and token management
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from ..models.user import UserService, UserCreate, UserInDB
from ..auth.jwt_handler import generate_tokens, verify_refresh_token
from ..utils.response_helper import send_error, send_auth_error

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user
        Returns user data and tokens
        """
        try:
            logger.info(f"Starting registration for email: {user_data.email}")

            # Create user (includes existence check)
            logger.info("Creating new user...")
            user = await UserService.create_user(user_data)
            logger.info(f"User created successfully with ID: {user.id}")

            # Generate tokens
            logger.info("Generating JWT tokens...")
            tokens = generate_tokens({
                "_id": str(user.id),
                "email": user.email,
                "name": user.name
            })
            logger.info("JWT tokens generated successfully")

            # Return user profile and tokens
            logger.info("Converting user to profile...")
            user_profile = UserService.to_profile(user)
            logger.info("User profile created successfully")

            logger.info("Serializing user profile...")
            user_dict = user_profile.model_dump(mode='json')
            logger.info("User profile serialized successfully")

            result = {
                "user": user_dict,
                "tokens": tokens
            }
            logger.info("Registration completed successfully")
            return result

        except ValueError as e:
            # Handle user already exists error
            logger.warning(f"Registration failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Registration failed with error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    @staticmethod
    async def login_user(email: str, password: str) -> Dict[str, Any]:
        """
        Login user with email and password
        Returns user data and tokens
        """
        # Find user by email
        user = await UserService.find_by_email_with_password(email)
        if not user:
            send_auth_error("Invalid email or password")

        # Verify password
        if not UserService.verify_password(user, password):
            send_auth_error("Invalid email or password")

        # Generate tokens
        tokens = generate_tokens({
            "_id": str(user.id),
            "email": user.email,
            "name": user.name
        })

        # Return user profile and tokens
        user_profile = UserService.to_profile(user)
        return {
            "user": user_profile.model_dump(mode='json'),
            "tokens": tokens
        }
    
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        Returns new tokens
        """
        try:
            # Verify refresh token
            payload = verify_refresh_token(refresh_token)
            user_id = payload.get("id")

            if not user_id:
                send_auth_error("Invalid refresh token")

            # Get user from database
            user = await UserService.find_by_id(user_id)
            if not user:
                send_auth_error("User not found")

            # Generate new tokens
            tokens = generate_tokens({
                "_id": str(user.id),
                "email": user.email,
                "name": user.name
            })

            user_profile = UserService.to_profile(user)
            return {
                "user": user_profile.model_dump(mode='json'),
                "tokens": tokens
            }

        except ValueError:
            send_auth_error("Invalid refresh token")
        except Exception:
            send_error("Token refresh failed", 500)
    
    @staticmethod
    async def get_user_profile(user_id: str) -> Dict[str, Any]:
        """
        Get user profile by ID
        """
        user = await UserService.find_by_id(user_id)
        if not user:
            send_error("User not found", 404)

        user_profile = UserService.to_profile(user)
        return {
            "user": user_profile.model_dump(mode='json')
        }
