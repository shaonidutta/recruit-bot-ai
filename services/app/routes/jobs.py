"""
Jobs Routes
New routes for job management and discovery
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..models.job import JobService, JobResponse, JobCreate, JobUpdate
from ..models.user import UserInDB
from ..auth.dependencies import get_current_user
from ..utils.response_helper import send_success, send_error, send_not_found_error

router = APIRouter()

@router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get list of jobs with pagination and search
    GET /api/jobs
    """
    try:
        if search:
            jobs = await JobService.search_jobs(search, skip, limit)
        else:
            jobs = await JobService.find_all(skip, limit, active_only)
        
        job_responses = [JobService.to_response(job) for job in jobs]
        total_count = await JobService.count_jobs(active_only)
        
        return send_success(
            data={
                "jobs": job_responses,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": total_count,
                    "has_more": skip + limit < total_count
                }
            },
            message="Jobs retrieved successfully"
        )
    except Exception as e:
        send_error("Failed to retrieve jobs", 500)

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get specific job by ID
    GET /api/jobs/{job_id}
    """
    try:
        job = await JobService.find_by_id(job_id)
        if not job:
            send_not_found_error("Job not found")
        
        return send_success(
            data={"job": JobService.to_response(job)},
            message="Job retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        send_error("Failed to retrieve job", 500)

@router.post("/jobs")
async def create_job(
    job_data: JobCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new job
    POST /api/jobs
    """
    try:
        job = await JobService.create_job(job_data)
        return send_success(
            data={"job": JobService.to_response(job)},
            message="Job created successfully",
            status_code=201
        )
    except Exception as e:
        send_error("Failed to create job", 500)

@router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update job by ID
    PUT /api/jobs/{job_id}
    """
    try:
        job = await JobService.update_job(job_id, job_data)
        if not job:
            send_not_found_error("Job not found")
        
        return send_success(
            data={"job": JobService.to_response(job)},
            message="Job updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        send_error("Failed to update job", 500)

@router.get("/jobs/stats/summary")
async def get_job_stats(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get job statistics summary
    GET /api/jobs/stats/summary
    """
    try:
        total_jobs = await JobService.count_jobs(active_only=False)
        active_jobs = await JobService.count_jobs(active_only=True)
        
        return send_success(
            data={
                "stats": {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "inactive_jobs": total_jobs - active_jobs
                }
            },
            message="Job statistics retrieved successfully"
        )
    except Exception as e:
        send_error("Failed to retrieve job statistics", 500)
