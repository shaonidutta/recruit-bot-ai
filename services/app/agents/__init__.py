# # This file makes the agents folder a Python package
# from fastapi import APIRouter
# from .linkedin_agent import router as linkedin_router
# from .indeed_agent import router as indeed_router

# router = APIRouter()
# router.include_router(linkedin_router)
# router.include_router(indeed_router)


from .linkedin_agent import fetch_linkedin_jobs
from .indeed_agent import fetch_indeed_jobs

__all__ = ['fetch_linkedin_jobs', 'fetch_indeed_jobs']