# services/app/services.py

from typing import List, Dict, Any
from .scraping_service import scrape_indeed_jobs
from .parsing_service import parse_job_description
from .enrichment_service import enrich_job, enrich_company, find_hiring_contacts


async def complete_job_discovery_workflow(job_title: str, location: str = None) -> List[Dict[str, Any]]:
    """
    Complete workflow: Scrape jobs from Indeed, parse descriptions, and enrich with company data.
    
    Args:
        job_title: The job title to search for
        location: Optional location filter
    
    Returns:
        List of enriched job postings with company info and contacts
    """
    # Step 1: Scrape jobs from Indeed
    raw_jobs = await scrape_indeed_jobs(job_title)
    
    enriched_jobs = []
    
    for job in raw_jobs:
        try:
            # Step 2: Parse job description if available
            if job.get('description'):
                parsed_data = parse_job_description(job['description'])
                job.update(parsed_data)
            
            # Step 3: Enrich with company information and contacts
            enriched_job = enrich_job(job)
            enriched_jobs.append(enriched_job)
            
        except Exception as e:
            # If enrichment fails, still include the basic job data
            print(f"Error enriching job {job.get('title', 'Unknown')}: {str(e)}")
            enriched_jobs.append(job)
    
    return enriched_jobs


async def analyze_company_hiring_pipeline(company_name: str) -> Dict[str, Any]:
    """
    Comprehensive company analysis including company info and hiring contacts.
    
    Args:
        company_name: Name of the company to analyze
    
    Returns:
        Dictionary with company information and hiring contacts
    """
    # Get company information
    company_info = enrich_company(company_name)
    
    # Get hiring contacts (recruiters, HR, talent acquisition)
    hiring_contacts = []
    contact_roles = ["Recruiter", "Talent Acquisition", "HR Manager", "Human Resources"]
    
    for role in contact_roles:
        contacts = find_hiring_contacts(company_name, role)
        for contact in contacts:
            contact['search_role'] = role
            hiring_contacts.append(contact)
    
    return {
        "company_info": company_info,
        "hiring_contacts": hiring_contacts,
        "total_contacts_found": len(hiring_contacts)
    }


async def job_application_prep(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare comprehensive data for job application including company research and contacts.
    
    Args:
        job_data: Basic job information (title, company, description, etc.)
    
    Returns:
        Complete application preparation data
    """
    company_name = job_data.get('company_name') or job_data.get('company')
    
    if not company_name:
        return {"error": "Company name not found in job data"}
    
    # Parse job description if available
    parsed_job = job_data.copy()
    if job_data.get('description'):
        parsed_data = parse_job_description(job_data['description'])
        parsed_job.update(parsed_data)
    
    # Get company analysis
    company_analysis = await analyze_company_hiring_pipeline(company_name)
    
    # Enrich the job with all available data
    enriched_job = enrich_job(parsed_job)
    
    return {
        "job_details": enriched_job,
        "company_analysis": company_analysis,
        "application_ready": True
    }