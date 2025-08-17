# services/app/routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

# Import your "chef" functions from the service files
from .scraping_service import scrape_indeed_jobs
from .parsing_service import parse_job_description
from .enrichment_service import enrich_job, enrich_company, find_hiring_contacts, verify_email
from .services import complete_job_discovery_workflow, analyze_company_hiring_pipeline, job_application_prep

# This is the router, like a menu board
router = APIRouter()

# --- Pydantic Models (Defines the structure of your API requests) ---


class JobDiscoveryRequest(BaseModel):
    job_title: str


class JobParseRequest(BaseModel):
    raw_description: str


class JobEnrichmentRequest(BaseModel):
    job: Dict[str, Any]


class CompanyEnrichmentRequest(BaseModel):
    company_name: str


class ContactSearchRequest(BaseModel):
    company_name: str
    job_title: str = "Recruiter"


class EmailVerificationRequest(BaseModel):
    email: str


class CompleteWorkflowRequest(BaseModel):
    job_title: str
    location: str = None


class CompanyAnalysisRequest(BaseModel):
    company_name: str


class JobApplicationPrepRequest(BaseModel):
    job_data: Dict[str, Any]


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


@router.post("/enrich/job", response_model=Dict[str, Any])
async def enrich_job_endpoint(request: JobEnrichmentRequest):
    """
    Enriches a job posting with company information and hiring contacts.
    """
    enriched_job = enrich_job(request.job)
    return enriched_job


@router.post("/enrich/company", response_model=Dict[str, Any])
async def enrich_company_endpoint(request: CompanyEnrichmentRequest):
    """
    Fetches detailed company information from Apollo.io.
    """
    company_info = enrich_company(request.company_name)
    return company_info or {"error": "Company not found"}


@router.post("/enrich/contacts", response_model=List[Dict])
async def find_contacts_endpoint(request: ContactSearchRequest):
    """
    Finds hiring contacts for a specific company.
    """
    contacts = find_hiring_contacts(request.company_name, request.job_title)
    return contacts


@router.post("/verify/email", response_model=Dict[str, Any])
async def verify_email_endpoint(request: EmailVerificationRequest):
    """
    Verifies email deliverability using Snov.io.
    """
    verification_result = verify_email(request.email)
    return verification_result or {"error": "Email verification failed"}


# --- Comprehensive Workflow Endpoints ---

@router.post("/workflow/complete-discovery", response_model=List[Dict[str, Any]])
async def complete_discovery_workflow_endpoint(request: CompleteWorkflowRequest):
    """
    Complete job discovery workflow: scrape, parse, and enrich jobs.
    """
    enriched_jobs = await complete_job_discovery_workflow(request.job_title, request.location)
    return enriched_jobs


@router.post("/workflow/company-analysis", response_model=Dict[str, Any])
async def company_analysis_endpoint(request: CompanyAnalysisRequest):
    """
    Comprehensive company analysis with hiring contacts.
    """
    analysis = await analyze_company_hiring_pipeline(request.company_name)
    return analysis


@router.post("/workflow/application-prep", response_model=Dict[str, Any])
async def application_prep_endpoint(request: JobApplicationPrepRequest):
    """
    Prepare comprehensive data for job application.
    """
    prep_data = await job_application_prep(request.job_data)
    return prep_data
