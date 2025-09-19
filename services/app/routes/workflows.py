"""
Simple Workflow Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.unified_orchestrator import run_unified_workflow
from ..utils.caching import cache_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/test-no-auth")
async def test_workflow_no_auth():
    """Test workflow without authentication"""
    try:
        logger.info("🔥 DEBUG: API ENDPOINT CALLED!")
        logger.info("🔥 DEBUG: About to call run_unified_workflow...")

        result = await run_unified_workflow(keywords="Python Developer")

        logger.info(f"🔥 DEBUG: Workflow completed! Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")

        return {
            "success": True,
            "message": "Test workflow completed",
            "data": result
        }
    except Exception as e:
        logger.error(f"🔥 DEBUG: WORKFLOW EXCEPTION: {e}")
        import traceback
        logger.error(f"🔥 DEBUG: TRACEBACK: {traceback.format_exc()}")
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

@router.post("/clear-cache")
async def clear_cache():
    """Clear all workflow caches"""
    try:
        await cache_manager.clear_all()
        stats = await cache_manager.get_all_stats()
        return {
            "success": True,
            "message": "All caches cleared successfully",
            "data": {
                "cache_stats": stats,
                "cleared_at": "now"
            }
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
