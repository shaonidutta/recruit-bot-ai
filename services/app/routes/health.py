"""
Health Check Routes
Converted from backend/src/routes/healthRoutes.js
System health and database connectivity checks
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from ..config.database import get_connection_status, is_connected
from ..utils.response_helper import send_success, send_error

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    GET /health
    """
    try:
        return send_success(
            data={
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "service": "AI Recruitment Agent API",
                "version": "1.0.0"
            },
            message="Service is healthy"
        )
    except Exception as e:
        return send_error("Health check failed", 500)

@router.get("/db")
async def database_health():
    """
    Database connectivity check
    GET /health/db
    """
    try:
        db_status = await get_connection_status()

        if db_status == "connected":
            return send_success(
                data={
                    "database": {
                        "status": "connected",
                        "type": "MongoDB",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                message="Database is connected"
            )
        else:
            return send_error("Database is not connected", 503)

    except Exception as e:
        return send_error("Database health check failed", 500)

@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check with all system components
    GET /health/detailed
    """
    try:
        db_status = await get_connection_status()
        
        health_data = {
            "service": {
                "name": "AI Recruitment Agent API",
                "version": "1.0.0",
                "status": "healthy",
                "uptime": "running"
            },
            "database": {
                "type": "MongoDB",
                "status": db_status,
                "connected": is_connected()
            },
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }
        
        # Overall status
        overall_status = "healthy" if db_status == "connected" else "degraded"
        status_code = 200 if overall_status == "healthy" else 503
        
        return send_success(
            data=health_data,
            message=f"System status: {overall_status}"
        )

    except Exception as e:
        return send_error("Detailed health check failed", 500)
