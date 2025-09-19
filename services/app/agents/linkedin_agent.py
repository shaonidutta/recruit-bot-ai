import os
from serpapi import GoogleSearch
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("❌ SERPAPI_KEY is not set. Please add it to your .env file.")


async def fetch_linkedin_jobs(job_title: str) -> List[Dict]:
    """
    Fetch LinkedIn jobs using SerpAPI (Google Jobs Engine).
    """
    print(f"Fetching LinkedIn jobs for: {job_title}")

    params = {
        "engine": "google_jobs",
        "q": job_title,
        "location": "United States",
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_data = results.get("jobs_results", [])

    # Debug: Print summary
    print(f"🔍 SerpAPI response: {len(jobs_data)} total jobs found")

    jobs = []

    for job in jobs_data:
        # Include all jobs from SerpAPI, not just LinkedIn-specific ones
        # This gives us more comprehensive job coverage
        job_data = {
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "description": job.get("description"),
            "via": job.get("via"),
            "source": "linkedin_search",  # Mark as coming from LinkedIn search
        }
        # Only include jobs with valid title and company
        if job_data["title"] and job_data["company"]:
            jobs.append(job_data)
        else:
            print(f"⚠️ Skipping job with missing data: {job_data}")

    print(f"✅ Found {len(jobs)} LinkedIn jobs.")
    return jobs
