import os
from serpapi import GoogleSearch
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY is not set. Please add it to your .env file.")


async def fetch_indeed_jobs(job_title: str) -> List[Dict]:
    """
    Fetch Indeed jobs using SerpAPI (Google Jobs Engine).
    """
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
        # Include all jobs from SerpAPI, not just Indeed-specific ones
        # This gives us more comprehensive job coverage
        job_data = {
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "description": job.get("description"),
            "via": job.get("via"),
            "source": "indeed_search",  # Mark as coming from Indeed search
        }
        # Only include jobs with valid title and company
        if job_data["title"] and job_data["company"]:
            jobs.append(job_data)
        else:
            print(f"⚠️ Skipping job with missing data: {job_data}")

    print(f"✅ Found {len(jobs)} Indeed jobs.")
    return jobs
