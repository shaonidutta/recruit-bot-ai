# services/app/routes.py

from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List, Dict, Any

from .agents.indeed_agent import fetch_indeed_jobs
from .agents.linkedin_agent import fetch_linkedin_jobs
from .agents.google_agent import fetch_google_jobs

# Import your "chef" functions from the service files
from .scraping_service import scrape_indeed_jobs

# This is the router, like a menu board
router = APIRouter()

# --- Pydantic Models (Defines the structure of your API requests) ---


class JobDiscoveryRequest(BaseModel):
    job_title: str


# --- API Endpoints (The items on your menu) ---

@router.post("/discover/indeed", response_model=List[Dict])
async def discover_indeed_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the Indeed Scraper Agent.
    """
    jobs = await fetch_indeed_jobs(request.job_title)
    return jobs


@router.post("/discover/linkedin", response_model=List[Dict])
async def discover_linkedin_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the LinkedIn Scraper Agent.
    """
    jobs = await fetch_linkedin_jobs(request.job_title)
    return jobs


@router.post("/discover/google", response_model=List[Dict])
async def discover_google_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the Google Scraper Agent.
    """
    jobs = await fetch_google_jobs(request.job_title)
    return jobs



router.get(
    "/agents/linkedin",
    status_code=status.HTTP_200_OK
)(fetch_linkedin_jobs)

router.get(
    "/agents/indeed",
    status_code=status.HTTP_200_OK
)(fetch_indeed_jobs)

router.get(
    "/agents/google",
    status_code=status.HTTP_200_OK
)(fetch_google_jobs)
