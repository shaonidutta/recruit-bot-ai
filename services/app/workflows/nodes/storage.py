"""
Simple Job Storage Node
"""

import logging
from typing import Dict, Any

from ...models.job import JobService, JobCreate
from ...models.match import MatchService

logger = logging.getLogger(__name__)

async def storage_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Store jobs and matches to database with comprehensive error handling"""
    logger.info("Starting enhanced storage with error handling")

    # Store matched jobs (which contain the match data)
    matched_jobs = state.get("matched_jobs", [])
    enriched_jobs = state.get("enriched_jobs", [])

    # Use matched_jobs if available (contains match data), otherwise fall back to enriched_jobs
    jobs_to_store = matched_jobs if matched_jobs else enriched_jobs

    print(f"🔍 DEBUG STORAGE: Available state keys: {list(state.keys())}")
    print(f"🔍 DEBUG STORAGE: Matched jobs: {len(matched_jobs)}")
    print(f"🔍 DEBUG STORAGE: Enriched jobs: {len(enriched_jobs)}")
    print(f"🔍 DEBUG STORAGE: Jobs to store: {len(jobs_to_store)}")

    logger.info(f"Jobs to store: {len(jobs_to_store)} ({'matched_jobs' if matched_jobs else 'enriched_jobs'})")

    # Debug: Check what data we're about to store
    if jobs_to_store:
        sample_job = jobs_to_store[0]
        logger.info(f"Sample job: {sample_job.get('title', 'Unknown')} with {len(sample_job.get('matches', []))} matches")

    if not jobs_to_store:
        state["stored_jobs"] = []
        logger.info("💾 No jobs to store")
        return state

    # Validate database connection
    try:
        from ...config.database import get_database, is_connected

        # Check if database is connected
        if not is_connected():
            raise Exception("Database not connected")

        db = get_database()
        if db is None:
            raise Exception("Database instance is None")

        job_service = JobService()
        match_service = MatchService()

        # Test database connection
        test_collection = job_service.get_collection()
        if test_collection is None:
            raise Exception("Job collection is None")

        await test_collection.count_documents({}, limit=1)
        logger.info("✅ Database connection verified")

    except Exception as db_error:
        logger.error(f"❌ Database connection failed: {db_error}")
        state["stored_jobs"] = []
        state["storage_error"] = f"Database connection failed: {str(db_error)}"
        return state

    stored_jobs = []

    # Counters for tracking
    new_jobs_count = 0
    duplicate_jobs_count = 0
    failed_jobs_count = 0
    total_matches_stored = 0
    total_matches_failed = 0

    for job in jobs_to_store:
        try:
            # Validate required job fields
            if not job.get("title") or not job.get("company"):
                logger.warning(f"⚠️ Skipping job with missing title or company: {job.get('title', 'No title')} at {job.get('company', 'No company')}")
                job["storage_status"] = "failed"
                job["storage_error"] = "Missing required fields (title or company)"
                stored_jobs.append(job)
                failed_jobs_count += 1
                continue

            # Prepare job data with enhanced salary and skills fields
            job_data = JobCreate(
                title=job.get("title"),
                company=job.get("company"),
                location=job.get("location"),
                description=job.get("description"),
                url=job.get("url") or job.get("apply_link") or None,
                salary_range=job.get("salary_range"),
                skills_required=job.get("skills_required", []),
                experience_level=job.get("experience_level"),
                via=job.get("source", "unknown"),
                company_id=job.get("company_id"),
                company_data=job.get("company_data"),
                workflow_id=state.get("workflow_id"),
                # NEW: Enhanced salary and skills fields
                min_salary=job.get("min_salary"),
                max_salary=job.get("max_salary"),
                salary_type=job.get("salary_type"),
                currency=job.get("currency", "USD"),
                equity_mentioned=job.get("equity_mentioned", False),
                benefits_mentioned=job.get("benefits_mentioned", False),
                technical_skills=job.get("technical_skills", []),
                frameworks=job.get("frameworks", []),
                databases=job.get("databases", []),
                cloud_platforms=job.get("cloud_platforms", []),
                tools=job.get("tools", []),
                methodologies=job.get("methodologies", []),
                soft_skills=job.get("soft_skills", []),
                experience_years_required=job.get("experience_years_required"),
                education_requirements=job.get("education_requirements", [])
            )

            # Create job with deduplication check
            stored_job, is_new = await job_service.create_job_with_deduplication(job_data)

            if is_new:
                new_jobs_count += 1
                logger.info(f"✅ New job stored: {job.get('title')} at {job.get('company')}")
            else:
                duplicate_jobs_count += 1
                logger.info(f"🔄 Duplicate job found: {job.get('title')} at {job.get('company')} (using existing)")

            # Store the job reference
            stored_job = stored_job

            # Store matches with proper error handling
            matches = job.get("matches", [])
            matches_stored = 0
            matches_failed = 0

            # DEBUG: Log match data for this job
            logger.info(f"🔍 DEBUG STORAGE: Job '{job.get('title')}' has {len(matches)} matches to store")
            if matches:
                logger.info(f"🔍 DEBUG STORAGE: First match data: {matches[0]}")
                print(f"🔍 DEBUG STORAGE MATCH: Job '{job.get('title')}' has {len(matches)} matches")
                print(f"🔍 DEBUG STORAGE MATCH: First match: {matches[0]}")
            else:
                print(f"🔍 DEBUG STORAGE MATCH: Job '{job.get('title')}' has NO matches")

            for match in matches:
                try:
                    # Validate required match data
                    if not match.get("candidate_id"):
                        logger.warning(f"⚠️ Skipping match with missing candidate_id for job {job.get('title')}")
                        matches_failed += 1
                        continue

                    match_data = {
                        "job_id": str(stored_job.id),
                        "candidate_id": match.get("candidate_id"),
                        "match_score": float(match.get("score", 0.0)),
                        "match_reasons": match.get("reasons", [])
                    }

                    # Validate match score
                    if not (0.0 <= match_data["match_score"] <= 1.0):
                        logger.warning(f"⚠️ Invalid match score {match_data['match_score']} for candidate {match_data['candidate_id']}")
                        match_data["match_score"] = max(0.0, min(1.0, match_data["match_score"]))

                    await match_service.create_match(match_data)
                    matches_stored += 1
                    total_matches_stored += 1
                    logger.debug(f"✅ Stored match: Job {stored_job.id} -> Candidate {match_data['candidate_id']} (Score: {match_data['match_score']:.2f})")

                except Exception as match_error:
                    matches_failed += 1
                    total_matches_failed += 1
                    logger.error(f"❌ Failed to store match for job {job.get('title')} -> candidate {match.get('candidate_id', 'Unknown')}: {match_error}")
                    continue

            # Log match storage results
            if matches:
                logger.info(f"📊 Match storage for {job.get('title')}: {matches_stored} stored, {matches_failed} failed")

            job["stored_job_id"] = str(stored_job.id)
            job["storage_status"] = "success"
            stored_jobs.append(job)

        except Exception as e:
            failed_jobs_count += 1
            logger.error(f"❌ Failed to store job {job.get('title', 'Unknown')}: {e}")
            job["storage_status"] = "failed"
            job["storage_error"] = str(e)
            stored_jobs.append(job)

    state["stored_jobs"] = stored_jobs
    successful_count = sum(1 for job in stored_jobs if job.get("storage_status") == "success")

    # Enhanced logging with comprehensive stats
    logger.info(f"💾 Enhanced storage completed:")
    logger.info(f"   📊 Jobs: {len(stored_jobs)} processed, {successful_count} successful, {failed_jobs_count} failed")
    logger.info(f"   🆕 New jobs created: {new_jobs_count}")
    logger.info(f"   🔄 Duplicates found: {duplicate_jobs_count}")
    logger.info(f"   🎯 Matches: {total_matches_stored} stored, {total_matches_failed} failed")

    # Add comprehensive stats to state for frontend display
    if "stats" not in state:
        state["stats"] = {}
    state["stats"].update({
        "new_jobs_stored": new_jobs_count,
        "duplicate_jobs_found": duplicate_jobs_count,
        "failed_jobs_count": failed_jobs_count,
        "total_jobs_processed": len(stored_jobs),
        "successful_jobs_count": successful_count,
        "matches_stored": total_matches_stored,
        "matches_failed": total_matches_failed
    })

    return state
