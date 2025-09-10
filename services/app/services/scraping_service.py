# services/app/scraping_service.py

import os
from serpapi import GoogleSearch
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY is not set. Please add it to your .env file.")


async def scrape_indeed_jobs(job_title: str) -> List[Dict]:
    """Fetch Indeed jobs using SerpAPI (Google Jobs Engine)."""
    print(f"Fetching Indeed jobs for: {job_title}")

    params = {
        "engine": "google_jobs",
        "q": job_title,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_data = results.get("jobs_results", [])
    jobs = []

    for job in jobs_data:
        if "indeed" in str(job.get("via", "")).lower():
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "via": job.get("via"),
                "source": "indeed"
            })

    print(f"✅ Found {len(jobs)} Indeed jobs.")
    return jobs


async def scrape_linkedin_jobs(job_title: str) -> List[Dict]:
    """
    Fetch LinkedIn jobs using SerpAPI (Google Jobs Engine).
    """
    print(f"Fetching LinkedIn jobs for: {job_title}")

    params = {
        "engine": "google_jobs",
        "q": job_title,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_data = results.get("jobs_results", [])
    jobs = []

    for job in jobs_data:
        if "linkedin" in str(job.get("via", "")).lower():
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "via": job.get("via"),
                "source": "linkedin"
            })

    print(f"✅ Found {len(jobs)} LinkedIn jobs.")
    return jobs


async def scrape_google_jobs(job_title: str) -> List[Dict]:
    """
    Fetch Google jobs using SerpAPI (Google Jobs Engine).
    """
    print(f"Fetching Google jobs for: {job_title}")

    params = {
        "engine": "google_jobs",
        "q": job_title,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_data = results.get("jobs_results", [])
    jobs = []

    for job in jobs_data:
        # Get all jobs that are not from indeed or linkedin
        via = str(job.get("via", "")).lower()
        if "indeed" not in via and "linkedin" not in via:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "via": job.get("via"),
                "source": "google"
            })

    print(f"✅ Found {len(jobs)} Google jobs.")
    return jobs
