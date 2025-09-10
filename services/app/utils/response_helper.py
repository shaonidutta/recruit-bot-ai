"""
Standardized API Response Helper
Converted from backend/src/utils/responseHelper.js
Provides consistent response format across all endpoints
"""
from datetime import datetime
from typing import Any, Optional, Dict, NoReturn
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def create_response(
    success: bool,
    message: str,
    data: Any = None,
    error: Any = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """Create standardized response format"""
    return {
        "success": success,
        "message": message,
        "data": data,
        "error": error,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def send_success(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Send success response"""
    return JSONResponse(
        status_code=status_code,
        content=create_response(
            success=True,
            message=message,
            data=data,
            error=None
        )
    )

def send_error(
    message: str = "Internal Server Error",
    status_code: int = 500,
    error: Any = None
) -> NoReturn:
    """Send error response"""
    raise HTTPException(
        status_code=status_code,
        detail=create_response(
            success=False,
            message=message,
            data=None,
            error=error or message
        )
    )

def send_validation_error(
    errors: list,
    message: str = "Validation failed"
) -> NoReturn:
    """Send validation error response"""
    raise HTTPException(
        status_code=422,
        detail=create_response(
            success=False,
            message=message,
            data=None,
            error={
                "type": "ValidationError",
                "details": errors
            }
        )
    )

def send_auth_error(message: str = "Authentication failed") -> NoReturn:
    """Send authentication error response"""
    raise HTTPException(
        status_code=401,
        detail=create_response(
            success=False,
            message=message,
            data=None,
            error={
                "type": "AuthenticationError",
                "details": message
            }
        )
    )

def send_authorization_error(message: str = "Access denied") -> NoReturn:
    """Send authorization error response"""
    raise HTTPException(
        status_code=403,
        detail=create_response(
            success=False,
            message=message,
            data=None,
            error={
                "type": "AuthorizationError",
                "details": message
            }
        )
    )

def send_not_found_error(message: str = "Resource not found") -> NoReturn:
    """Send not found error response"""
    raise HTTPException(
        status_code=404,
        detail=create_response(
            success=False,
            message=message,
            data=None,
            error={
                "type": "NotFoundError",
                "details": message
            }
        )
    )
