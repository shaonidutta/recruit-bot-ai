"""
Jobs Routes
New routes for job management and discovery
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
import logging
from ..models.job import JobService, JobResponse, JobCreate, JobUpdate
from ..models.candidate import CandidateService
from ..models.user import UserInDB
from ..auth.dependencies import get_current_user
from ..utils.response_helper import send_success, send_error, send_not_found_error

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/jobs")
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(True),
    search: Optional[str] = Query(None)
):
    """
    Get list of jobs with pagination and search
    GET /api/jobs
    """
    try:
        logger.info(f"Getting jobs: skip={skip}, limit={limit}, active_only={active_only}, search={search}")

        try:
            if search:
                jobs = await JobService.search_jobs(search, skip, limit)
            else:
                jobs = await JobService.find_all(skip, limit, active_only)
        except ConnectionError:
            logger.warning("Database connection not available - returning empty job list")
            return send_success(
                data={
                    "jobs": [],
                    "total": 0,
                    "skip": skip,
                    "limit": limit,
                    "has_more": False
                },
                message="Jobs retrieved (database offline - no data available)"
            )

        logger.info(f"Retrieved {len(jobs)} jobs from database")

        job_responses = [JobService.to_response(job).model_dump(mode='json') for job in jobs]
        total_count = await JobService.count_jobs(active_only)

        logger.info(f"Successfully processed {len(job_responses)} job responses, total_count={total_count}")

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
        logger.error(f"Error retrieving jobs: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve jobs: {str(e)}", 500)

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
            data={"job": JobService.to_response(job).dict()},
            message="Job retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return send_error("Failed to retrieve job", 500)

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
            data={"job": JobService.to_response(job).dict()},
            message="Job created successfully",
            status_code=201
        )
    except Exception as e:
        return send_error("Failed to create job", 500)

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
            data={"job": JobService.to_response(job).dict()},
            message="Job updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return send_error("Failed to update job", 500)

@router.get("/jobs/stats/summary")
async def get_job_stats():
    """
    Get job and candidate statistics summary
    GET /api/jobs/stats/summary
    """
    try:
        total_jobs = await JobService.count_jobs(active_only=False)
        active_jobs = await JobService.count_jobs(active_only=True)
        total_candidates = await CandidateService.count_candidates(active_only=False)
        active_candidates = await CandidateService.count_candidates(active_only=True)

        # Import MatchService here to avoid circular imports
        from ..models.match import MatchService
        total_matches = await MatchService.count_matches(active_only=True)

        return send_success(
            data={
                "stats": {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "inactive_jobs": total_jobs - active_jobs,
                    "total_candidates": total_candidates,
                    "active_candidates": active_candidates,
                    "inactive_candidates": total_candidates - active_candidates,
                    "total_matches": total_matches
                }
            },
            message="Statistics retrieved successfully"
        )
    except Exception as e:
        return send_error("Failed to retrieve statistics", 500)

# Matches endpoint moved to dedicated matches.py route file
# This endpoint is deprecated - use /api/v1/matches instead

@router.get("/recent-jobs")
async def get_recent_jobs(
    limit: int = Query(10, ge=1, le=100),
    workflow_id: Optional[str] = Query(None)
):
    """
    Get recent jobs from latest workflow run
    GET /api/jobs/recent?limit=10&workflow_id=unified_20250821_103521
    """
    try:
        try:
            # If no workflow_id provided, get the latest one
            if not workflow_id:
                workflow_id = await JobService.get_latest_workflow_id()
                if not workflow_id:
                    return send_success(
                        data={
                            "jobs": [],
                            "workflow_id": None,
                            "message": "No workflow runs found"
                        },
                        message="No recent jobs found"
                    )

            logger.info(f"Getting recent jobs for workflow_id: {workflow_id}")

            # Get jobs from the specified workflow
            jobs = await JobService.find_by_workflow_id(workflow_id, 0, limit)
            job_responses = [JobService.to_response(job).model_dump(mode='json') for job in jobs]

            logger.info(f"Found {len(job_responses)} recent jobs from workflow {workflow_id}")

            return send_success(
                data={
                    "jobs": job_responses,
                    "workflow_id": workflow_id,
                    "count": len(job_responses),
                    "limit": limit
                },
                message=f"Recent jobs retrieved successfully from workflow {workflow_id}"
            )
        except ConnectionError:
            logger.warning("Database connection not available - returning empty recent jobs")
            return send_success(
                data={
                    "jobs": [],
                    "workflow_id": None,
                    "count": 0,
                    "limit": limit
                },
                message="Recent jobs (database offline - no data available)"
            )
    except Exception as e:
        logger.error(f"Error retrieving recent jobs: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve recent jobs: {str(e)}", 500)
