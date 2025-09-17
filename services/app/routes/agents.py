"""
Simple Agent Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.unified_orchestrator import run_unified_workflow

router = APIRouter()

@router.post("/agent")
async def trigger_agent_discovery(request: Dict[str, Any]):
    """Trigger job discovery workflow"""
    try:
        keywords = request.get("keywords", "Software Engineer")
        result = await run_unified_workflow(keywords=keywords)
        return {
            "success": True,
            "message": "Job discovery completed",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoints for individual agents
@router.get("/agents/linkedin")
async def linkedin_agent_test(job_title: str = "Software Engineer"):
    """Test LinkedIn agent"""
    try:
        from ..agents.linkedin_agent import fetch_linkedin_jobs
        jobs = await fetch_linkedin_jobs(job_title)
        return {
            "success": True,
            "message": f"Found {len(jobs)} LinkedIn jobs",
            "data": {"jobs": jobs}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/indeed")
async def indeed_agent_test(job_title: str = "Software Engineer"):
    """Test Indeed agent"""
    try:
        from ..agents.indeed_agent import fetch_indeed_jobs
        jobs = await fetch_indeed_jobs(job_title)
        return {
            "success": True,
            "message": f"Found {len(jobs)} Indeed jobs",
            "data": {"jobs": jobs}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/google")
async def google_agent_test(job_title: str = "Software Engineer"):
    """Test Google agent"""
    try:
        from ..agents.google_agent import fetch_google_jobs
        jobs = await fetch_google_jobs(job_title)
        return {
            "success": True,
            "message": f"Found {len(jobs)} Google jobs",
            "data": {"jobs": jobs}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
