import os
from serpapi import GoogleSearch
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

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
            })

    print(f"✅ Found {len(jobs)} LinkedIn jobs.")
    return jobs
