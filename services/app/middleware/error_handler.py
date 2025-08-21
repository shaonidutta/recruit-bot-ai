"""
Global Error Handler Middleware
Converted from backend/src/middleware/errorHandler.js
Catches and handles all unhandled errors
"""
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError
from jose import JWTError
from ..utils.response_helper import create_response

logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI):
    """Add all exception handlers to the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        logger.error(f"HTTP Exception: {exc.detail}")
        
        # If detail is already in our response format, return it
        if isinstance(exc.detail, dict) and "success" in exc.detail:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail
            )
        
        # Otherwise, format it
        return JSONResponse(
            status_code=exc.status_code,
            content=create_response(
                success=False,
                message=str(exc.detail),
                data=None,
                error=str(exc.detail)
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.error(f"Validation Error: {errors}")
        
        return JSONResponse(
            status_code=422,
            content=create_response(
                success=False,
                message="Validation failed",
                data=None,
                error={
                    "type": "ValidationError",
                    "details": errors
                }
            )
        )
    
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
        """Handle MongoDB duplicate key errors"""
        logger.error(f"Duplicate Key Error: {exc}")
        
        # Extract field name from error message
        field = "field"
        if "email" in str(exc):
            field = "email"
            message = "Email already exists"
        else:
            message = "Duplicate value found"
        
        return JSONResponse(
            status_code=409,
            content=create_response(
                success=False,
                message=message,
                data=None,
                error={
                    "type": "DuplicateKeyError",
                    "field": field,
                    "details": message
                }
            )
        )
    
    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError):
        """Handle JWT errors"""
        logger.error(f"JWT Error: {exc}")
        
        if "expired" in str(exc).lower():
            message = "Token expired"
        else:
            message = "Invalid token"
        
        return JSONResponse(
            status_code=401,
            content=create_response(
                success=False,
                message=message,
                data=None,
                error={
                    "type": "JWTError",
                    "details": message
                }
            )
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors (often from JWT or validation)"""
        logger.error(f"Value Error: {exc}")
        
        if "token" in str(exc).lower():
            status_code = 401
            error_type = "AuthenticationError"
        else:
            status_code = 400
            error_type = "ValueError"
        
        return JSONResponse(
            status_code=status_code,
            content=create_response(
                success=False,
                message=str(exc),
                data=None,
                error={
                    "type": error_type,
                    "details": str(exc)
                }
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=create_response(
                success=False,
                message="Internal Server Error",
                data=None,
                error={
                    "type": "InternalServerError",
                    "details": "An unexpected error occurred"
                }
            )
        )
