"""
Simple Job Storage Node
"""

import logging
from typing import Dict, Any

from ...models.job import JobService, JobCreate
from ...models.match import MatchService

logger = logging.getLogger(__name__)

async def storage_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Store jobs and matches to database"""
    logger.info("💾 Starting storage")

    # Store ALL enriched jobs (not just matched ones)
    enriched_jobs = state.get("enriched_jobs", [])
    jobs_to_store = enriched_jobs

    if not jobs_to_store:
        state["stored_jobs"] = []
        logger.info("💾 No jobs to store")
        return state

    job_service = JobService()
    match_service = MatchService()
    stored_jobs = []

    for job in jobs_to_store:
        try:
            # Store job to database with company relationship and workflow tracking
            job_data = JobCreate(
                title=job.get("title"),
                company=job.get("company"),
                location=job.get("location"),
                description=job.get("description"),
                url=str(job.get("url") or "https://example.com/job"),  # Convert to string
                salary_range=job.get("salary_range"),
                skills_required=job.get("parsed_data", {}).get("skills_required", []),
                experience_level=job.get("parsed_data", {}).get("experience_level"),
                via=job.get("source", "unknown"),
                company_id=job.get("company_id"),  # NEW: Link to company
                company_data=job.get("company_data"),  # Keep for backward compatibility
                parsed_data=job.get("parsed_data"),
                workflow_id=state.get("workflow_id")  # NEW: Track which workflow discovered this job
            )
            stored_job = await job_service.create_job(job_data)

            # Store matches
            matches = job.get("matches", [])
            for match in matches:
                await match_service.create_match({
                    "job_id": str(stored_job.id),
                    "candidate_id": match.get("candidate_id"),
                    "match_score": match.get("score", 0.0),
                    "match_reasons": match.get("reasons", [])
                })

            job["stored_job_id"] = str(stored_job.id)
            job["storage_status"] = "success"
            stored_jobs.append(job)

        except Exception as e:
            logger.warning(f"Failed to store job {job.get('title', 'Unknown')}: {e}")
            job["storage_status"] = "failed"
            job["storage_error"] = str(e)
            stored_jobs.append(job)

    state["stored_jobs"] = stored_jobs
    successful_count = sum(1 for job in stored_jobs if job.get("storage_status") == "success")
    logger.info(f"✅ Stored {successful_count}/{len(stored_jobs)} jobs")

    return state
