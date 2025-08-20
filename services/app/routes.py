# services/app/routes.py
"""
FastAPI routes for AI Recruitment Agent services
Provides endpoints for job discovery, enrichment, matching, and workflow orchestration
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from .agents.indeed_agent import fetch_indeed_jobs
from .agents.linkedin_agent import fetch_linkedin_jobs
from .enrichment_service import get_enrichment_service
from .matching_service import get_matching_engine
from .parsing_service import parse_job_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/discover/indeed")
async def discover_indeed_jobs(job_title: str):
    """
    Discover jobs from Indeed
    Returns: Raw job data for backend to process and store
    """
    try:
        jobs = await fetch_indeed_jobs(job_title)

        return {
            "success": True,
            "message": f"Discovered {len(jobs)} Indeed jobs",
            "data": {
                "platform": "indeed",
                "job_title": job_title,
                "jobs_found": len(jobs),
                "jobs": jobs
            }
        }

    except Exception as e:
        logger.error(f"❌ Indeed discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover/linkedin")
async def discover_linkedin_jobs(job_title: str):
    """
    Discover jobs from LinkedIn
    Returns: Raw job data for backend to process and store
    """
    try:
        jobs = await fetch_linkedin_jobs(job_title)

        return {
            "success": True,
            "message": f"Discovered {len(jobs)} LinkedIn jobs",
            "data": {
                "platform": "linkedin",
                "job_title": job_title,
                "jobs_found": len(jobs),
                "jobs": jobs
            }
        }

    except Exception as e:
        logger.error(f"❌ LinkedIn discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Enrichment Endpoints ---

@router.post("/enrich/job")
async def enrich_job_data(job_data: Dict[str, Any]):
    """
    Enrich job data with company information
    Returns: Enriched data for backend to store
    """
    try:
        enrichment_service = await get_enrichment_service()
        company_name = job_data.get("company_name") or job_data.get("company")

        if not company_name:
            return {"success": False, "message": "No company name provided"}

        # Enrich company information
        company_data = await enrichment_service.enrich_company(company_name)

        return {
            "success": True,
            "message": f"Job enrichment completed for {company_name}",
            "data": {
                "job_data": job_data,
                "company_data": company_data
            }
        }

    except Exception as e:
        logger.error(f"❌ Job enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich/company")
async def enrich_company_data(company_name: str):
    """
    Enrich company information and find hiring contacts
    Returns: Company and contact data for backend to store
    """
    try:
        enrichment_service = await get_enrichment_service()

        # Enrich company information
        company_data = await enrichment_service.enrich_company(company_name)

        return {
            "success": True,
            "message": f"Company enrichment completed for {company_name}",
            "data": {
                "company_data": company_data
            }
        }

    except Exception as e:
        logger.error(f"❌ Company enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Matching Endpoints ---

@router.post("/match/candidates")
async def match_candidates_to_job(job_data: Dict[str, Any], candidates: List[Dict[str, Any]], min_score: float = 0.75):
    """
    Find candidate matches for a job
    Returns: Match data for backend to store
    """
    try:
        matching_engine = get_matching_engine()
        result = matching_engine.match_candidates_to_job(job_data, candidates, min_score)
        return result

    except Exception as e:
        logger.error(f"❌ Matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Processing Endpoints ---

@router.post("/parse/job")
async def parse_job_description_endpoint(request: Dict[str, Any]):
    """
    Parse job description to extract skills, requirements, etc.
    Returns: Parsed job data for backend to store
    """
    try:
        description = request.get("description", "")
        job_title = request.get("job_title", "")
        parsed_data = parse_job_description(description, job_title)

        return {
            "success": True,
            "message": "Job description parsed successfully",
            "data": parsed_data
        }

    except Exception as e:
        logger.error(f"❌ Job parsing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Health Check ---

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "success": True,
        "message": "AI Recruitment Services are running",
        "services": {
            "discovery": "✅ Available",
            "enrichment": "✅ Available",
            "parsing": "✅ Available",
            "matching": "✅ Available"
        }
    }


# --- Legacy Agent Endpoints (for backward compatibility) ---

@router.get("/agents/linkedin")
async def linkedin_agent_legacy(job_title: str = "Software Engineer"):
    """Legacy endpoint for LinkedIn agent"""
    return await fetch_linkedin_jobs(job_title)


@router.get("/agents/indeed")
async def indeed_agent_legacy(job_title: str = "Software Engineer"):
    """Legacy endpoint for Indeed agent"""
    return await fetch_indeed_jobs(job_title)
