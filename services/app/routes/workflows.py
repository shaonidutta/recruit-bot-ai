"""
Simple Workflow Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.unified_orchestrator import run_unified_workflow

router = APIRouter()

@router.post("/test-no-auth")
async def test_workflow_no_auth():
    """Test workflow without authentication"""
    try:
        result = await run_unified_workflow(keywords="Python Developer")
        return {
            "success": True,
            "message": "Test workflow completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run")
async def run_workflow(request: Dict[str, Any]):
    """Run the unified workflow"""
    try:
        keywords = request.get("keywords", "Software Engineer")
        result = await run_unified_workflow(keywords=keywords)
        return {
            "success": True,
            "message": "Workflow completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
