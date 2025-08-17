# services/app/routes.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import your "chef" functions from the service files
from .scraping_service import scrape_indeed_jobs
from .parsing_service import parse_job_description
from .enrichment_service import enrich_job, enrich_company, find_hiring_contacts, verify_email
from .services import complete_job_discovery_workflow, analyze_company_hiring_pipeline, job_application_prep

# Import new agents and services
from .agents.linkedin_agent import fetch_linkedin_jobs
from .agents.google_jobs_agent import fetch_google_jobs
from .agents.glassdoor_agent import fetch_glassdoor_jobs
from .services.content_generation_service import generate_personalized_email, generate_linkedin_message, generate_ab_test_variations
from .services.ab_testing_service import create_ab_test, start_ab_test, get_test_status, analyze_ab_test
from .services.matching_service import calculate_match_score, find_best_matches, analyze_skill_gaps
from .models import JobPosting, Candidate, OutreachTemplate

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


class ContentGenerationRequest(BaseModel):
    candidate: Dict[str, Any]
    job_posting: Dict[str, Any]
    template_type: str = "cold_outreach"
    tone: str = "professional"


class ABTestRequest(BaseModel):
    test_name: str
    test_type: str
    templates: List[Dict[str, Any]]
    minimum_sample_size: Optional[int] = 100
    confidence_level: Optional[float] = 0.95


class MatchingRequest(BaseModel):
    candidate: Dict[str, Any]
    job_posting: Dict[str, Any]


class BestMatchesRequest(BaseModel):
    candidate: Dict[str, Any]
    job_postings: List[Dict[str, Any]]
    top_k: Optional[int] = 10


class SkillGapRequest(BaseModel):
    candidate: Dict[str, Any]
    job_posting: Dict[str, Any]


# --- API Endpoints (The items on your menu) ---


@router.post("/discover/linkedin", response_model=Dict[str, Any])
async def discover_linkedin_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the LinkedIn Jobs Agent.
    """
    result = await fetch_linkedin_jobs(request.job_title)
    return result.dict() if hasattr(result, 'dict') else result


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


@router.post("/discover/glassdoor", response_model=Dict[str, Any])
async def discover_glassdoor_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the Glassdoor Scraper Agent.
    """
    result = await fetch_glassdoor_jobs(request.job_title)
    return result.dict() if hasattr(result, 'dict') else result


@router.post("/discover/google", response_model=Dict[str, Any])
async def discover_google_endpoint(request: JobDiscoveryRequest):
    """
    Triggers the Google Jobs Agent using SerpAPI.
    """
    result = await fetch_google_jobs(request.job_title)
    return result.dict() if hasattr(result, 'dict') else result


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


# --- Content Generation Endpoints ---

@router.post("/content/generate-email", response_model=Dict[str, Any])
async def generate_email_endpoint(request: ContentGenerationRequest):
    """
    Generate personalized email content using GPT-4.
    """
    email_content = await generate_personalized_email(
        candidate=request.candidate,
        job_posting=request.job_posting,
        template_type=request.template_type,
        tone=request.tone
    )
    return email_content


@router.post("/content/generate-linkedin", response_model=Dict[str, Any])
async def generate_linkedin_endpoint(request: ContentGenerationRequest):
    """
    Generate personalized LinkedIn message using GPT-4.
    """
    linkedin_content = await generate_linkedin_message(
        candidate=request.candidate,
        job_posting=request.job_posting,
        tone=request.tone
    )
    return linkedin_content


@router.post("/content/generate-variations", response_model=List[Dict[str, Any]])
async def generate_variations_endpoint(request: ContentGenerationRequest):
    """
    Generate multiple content variations for A/B testing.
    """
    variations = await generate_ab_test_variations(
        candidate=request.candidate,
        job_posting=request.job_posting,
        template_type=request.template_type,
        num_variations=3
    )
    return variations


# --- A/B Testing Endpoints ---

@router.post("/ab-test/create", response_model=Dict[str, Any])
async def create_ab_test_endpoint(request: ABTestRequest):
    """
    Create a new A/B test.
    """
    # Convert dict templates to OutreachTemplate objects
    templates = [OutreachTemplate(**template) for template in request.templates]
    
    test = create_ab_test(
        test_name=request.test_name,
        test_type=request.test_type,
        templates=templates,
        minimum_sample_size=request.minimum_sample_size,
        confidence_level=request.confidence_level
    )
    return {"test_id": test.test_id, "status": test.status.value}


@router.post("/ab-test/{test_id}/start", response_model=Dict[str, Any])
async def start_ab_test_endpoint(test_id: str):
    """
    Start an A/B test.
    """
    success = start_ab_test(test_id)
    return {"success": success, "test_id": test_id}


@router.get("/ab-test/{test_id}/status", response_model=Dict[str, Any])
async def get_ab_test_status_endpoint(test_id: str):
    """
    Get A/B test status and results.
    """
    status = get_test_status(test_id)
    return status or {"error": "Test not found"}


@router.get("/ab-test/{test_id}/analyze", response_model=Dict[str, Any])
async def analyze_ab_test_endpoint(test_id: str):
    """
    Analyze A/B test results.
    """
    results = analyze_ab_test(test_id)
    if results:
        return {
            "test_id": results.test_id,
            "winning_variant": results.winning_variant.variant_name,
            "confidence_level": results.confidence_level,
            "statistical_significance": results.statistical_significance,
            "improvement_percentage": results.improvement_percentage,
            "recommendation": results.recommendation,
            "detailed_metrics": results.detailed_metrics
        }
    return {"error": "Test results not available"}


# --- AI Matching Endpoints ---

@router.post("/matching/calculate-score", response_model=Dict[str, Any])
async def calculate_match_score_endpoint(request: MatchingRequest):
    """
    Calculate match score between candidate and job posting.
    """
    # Convert dicts to model objects
    candidate = Candidate(**request.candidate)
    job_posting = JobPosting(**request.job_posting)
    
    match_score = await calculate_match_score(candidate, job_posting)
    return match_score.dict() if hasattr(match_score, 'dict') else match_score


@router.post("/matching/find-best-matches", response_model=List[Dict[str, Any]])
async def find_best_matches_endpoint(request: BestMatchesRequest):
    """
    Find best job matches for a candidate.
    """
    # Convert dicts to model objects
    candidate = Candidate(**request.candidate)
    job_postings = [JobPosting(**job) for job in request.job_postings]
    
    matches = await find_best_matches(candidate, job_postings, request.top_k)
    return [match.dict() if hasattr(match, 'dict') else match for match in matches]


@router.post("/matching/skill-gap-analysis", response_model=Dict[str, Any])
async def skill_gap_analysis_endpoint(request: SkillGapRequest):
    """
    Analyze skill gaps between candidate and job requirements.
    """
    # Convert dicts to model objects
    candidate = Candidate(**request.candidate)
    job_posting = JobPosting(**request.job_posting)
    
    skill_gaps = await analyze_skill_gaps(candidate, job_posting)
    return skill_gaps
