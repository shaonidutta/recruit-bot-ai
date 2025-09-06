import os
from serpapi import GoogleSearch
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError(" SERPAPI_KEY is not set. Please add it to your .env file.")


async def fetch_indeed_jobs(job_title: str) -> List[Dict]:
    """
    Fetch Indeed jobs using SerpAPI (Google Jobs Engine).
    """
    print(f"Fetching Indeed jobs for: {job_title}")

    params = {
        "engine": "google_jobs",
        "q": job_title + " developer",  # Different search variation
        "hl": "en",
        "api_key": SERPAPI_KEY,
        "num": 10
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    jobs_data = results.get("jobs_results", [])
    jobs = []

    # Filter jobs that are actually from Indeed based on 'via' field
    for job in jobs_data:
        via = job.get("via", "").lower()
        # Only include jobs that are actually from Indeed
        if "indeed" in via:
            jobs.append({
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "description": job.get("description"),
                "via": job.get("via"),
                "source": "indeed",  # Now correctly assigned based on actual source
                "url": job.get("apply_link", "")
            })

    print(f" Found {len(jobs)} Indeed jobs.")
    return jobs
