from fastapi import APIRouter, status
from .agents.indeed_agent import fetch_indeed_jobs
from .agents.linkedin_agent import fetch_linkedin_jobs


# from agents.linkedin_agent import fetch_linkedin_jobs

router = APIRouter()

router.get(
    "/agents/linkedin",
    status_code=status.HTTP_200_OK
)(fetch_linkedin_jobs)

router.get(
    "/agents/indeed",
    status_code=status.HTTP_200_OK
)(fetch_indeed_jobs)