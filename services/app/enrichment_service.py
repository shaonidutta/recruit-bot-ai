import os
import requests
from dotenv import load_dotenv

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
SNOV_CLIENT_ID = os.getenv("SNOV_CLIENT_ID")
SNOV_CLIENT_SECRET = os.getenv("SNOV_CLIENT_SECRET")

# ---------------- Apollo.io ---------------- #

def enrich_company(company_name: str):
    """
    Fetch company details from Apollo.io API.
    """
    url = "https://api.apollo.io/v1/mixed_companies/search"
    headers = {"Cache-Control": "no-cache"}
    payload = {
        "api_key": APOLLO_API_KEY,
        "q_organization_name": company_name,
        "page": 1,
        "per_page": 1,
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        return None

    data = resp.json()
    if "organizations" in data and len(data["organizations"]) > 0:
        org = data["organizations"][0]
        return {
            "name": org.get("name"),
            "website": org.get("website_url"),
            "industry": org.get("industry"),
            "size": org.get("estimated_num_employees"),
            "linkedin": org.get("linkedin_url"),
            "founded": org.get("founded_year"),
            "city": org.get("city"),
            "country": org.get("country"),
        }
    return None


def find_hiring_contacts(company_name: str, job_title: str = "Recruiter"):
    """
    Fetch hiring manager or recruiter contacts from Apollo.io
    """
    url = "https://api.apollo.io/v1/people/match"
    payload = {
        "api_key": APOLLO_API_KEY,
        "q_organization_name": company_name,
        "title": job_title,  # e.g. Recruiter, Talent Acquisition, HR
        "page": 1,
        "per_page": 3
    }
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        return []

    data = resp.json()
    contacts = []
    for person in data.get("people", []):
        contacts.append({
            "name": f"{person.get('first_name')} {person.get('last_name')}",
            "title": person.get("title"),
            "email": person.get("email"),
            "linkedin": person.get("linkedin_url"),
        })
    return contacts


# ---------------- Snov.io (Email Verification) ---------------- #

def snov_get_access_token():
    url = "https://api.snov.io/v1/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": SNOV_CLIENT_ID,
        "client_secret": SNOV_CLIENT_SECRET,
    }
    resp = requests.post(url, data=payload)
    return resp.json().get("access_token")


def verify_email(email: str):
    """
    Verify email deliverability using Snov.io
    """
    token = snov_get_access_token()
    url = f"https://api.snov.io/v1/get-emails-verification-status?access_token={token}&emails[]={email}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data["data"][0] if "data" in data else None
    return None


# ---------------- High-Level API ---------------- #

def enrich_job(job: dict):
    """
    Takes a job dict from SerpAPI and enriches with company + contacts.
    """
    company_name = job.get("company_name")
    enriched = {
        "job_title": job.get("title"),
        "company": company_name,
        "location": job.get("location"),
        "job_url": job.get("link"),
    }

    # Add company info
    company_info = enrich_company(company_name)
    if company_info:
        enriched["company_info"] = company_info

    # Add recruiter contacts
    contacts = find_hiring_contacts(company_name)
    if contacts:
        enriched["contacts"] = []
        for c in contacts:
            email_status = verify_email(c["email"]) if c.get("email") else None
            c["email_status"] = email_status
            enriched["contacts"].append(c)

    return enriched
