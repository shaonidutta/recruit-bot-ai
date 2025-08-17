# services/app/routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

# Import your "chef" functions from the service files
from .scraping_service import scrape_indeed_jobs
from .parsing_service import parse_job_description

# This is the router, like a menu board
router = APIRouter()

# --- Pydantic Models (Defines the structure of your API requests) ---


class JobDiscoveryRequest(BaseModel):
    job_title: str


class JobParseRequest(BaseModel):
    raw_description: str


# --- API Endpoints (The items on your menu) ---


# @router.post("/discover/linkedin", response_model=List[Dict])
# async def discover_linkedin_endpoint(request: JobDiscoveryRequest):
#     """
#     Triggers the LinkedIn Jobs Agent.
#     """
#     jobs = await scrape_linkedin_jobs(request.job_title)
#     return jobs


@router.post("/discover/indeed", response_model=List[Dict])
async def discover_indeed_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the Indeed Scraper Agent.
    """
    jobs = await scrape_indeed_jobs(request.job_title)
    return jobs

# @router.post("/discover/indeed1", response_model=List[Dict])
# async def discover_indeed_endpoint1(request: JobDiscoveryRequest):
#     """
#     Triggers the Indeed Scraper Agent.
#     """
#     jobs = await scrape_indeed_with_playwright(request.job_title)
#     return jobs


# @router.post("/discover/glassdoor", response_model=List[Dict])
# async def discover_glassdoor_endpoint(request: JobDiscoveryRequest):
#     """
#     Triggers the Glassdoor Scraper Agent.
#     """
#     jobs = await scrape_glassdoor_jobs(request.job_title)
#     return jobs


# @router.post("/discover/google", response_model=List[Dict])
# async def discover_google_endpoint(request: JobDiscoveryRequest):
#     """
#     Triggers the Google Jobs Agent using SerpAPI.
#     """
#     jobs = await fetch_jobs_google(request.job_title)
#     return jobs


@router.post("/parse/job", response_model=Dict[str, Any])
async def parse_job_endpoint(request: JobParseRequest):
    """
    Parses a raw job description to extract structured data.
    """
    parsed_data = parse_job_description(request.raw_description)
    return parsed_data
