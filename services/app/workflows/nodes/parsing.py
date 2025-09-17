"""
Enhanced Job Parsing Node with Salary and Skills Extraction
Optimized with parallel processing for improved performance
"""

import logging
import asyncio
from typing import Dict, Any, List

from ...services.parsing_service import JobParsingService
from ...utils.parallel_processing import parallel_processor, performance_monitor

logger = logging.getLogger(__name__)

# Initialize parsing service
parsing_service = JobParsingService()


async def parse_single_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single job description - optimized for production performance"""
    try:
        # Extract description and title from job dictionary
        description = job.get("description", "")
        title = job.get("title", "")

        # Use parsing service with proper parameters
        parsed_data = await parsing_service.parse_job_description(description, title)

        # Merge parsed data with original job data
        result = job.copy()  # Keep original job data
        result.update(parsed_data)  # Add parsed data
        result["parsing_success"] = True

        return result
    except Exception as e:
        logger.error(f"Parsing failed for job {job.get('title', 'Unknown')}: {e}")
        job["parsing_success"] = False
        job["parsing_error"] = str(e)
        return job

@performance_monitor("Enhanced Parsing (Parallel)")
async def parsing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse job descriptions using parallel processing for optimal performance"""
    logger.info("Starting enhanced parsing with parallel processing")

    # Get jobs from the previous step (try multiple sources)
    jobs_to_parse = (
        state.get("enriched_jobs", []) or
        state.get("raw_jobs", []) or
        state.get("deduplicated_jobs", []) or
        []
    )

    print(f"🔍 DEBUG PARSING: Available state keys: {list(state.keys())}")
    print(f"🔍 DEBUG PARSING: Jobs to parse: {len(jobs_to_parse)}")
    logger.info(f"🔍 DEBUG Parsing - Available state keys: {list(state.keys())}")
    logger.info(f"🔍 DEBUG Parsing - Jobs to parse: {len(jobs_to_parse)}")

    # If still no jobs, try to aggregate from scraping results
    if not jobs_to_parse:
        all_jobs = []
        for job in state.get("linkedin_jobs", []):
            job["source"] = "linkedin"
            all_jobs.append(job)
        for job in state.get("indeed_jobs", []):
            job["source"] = "indeed"
            all_jobs.append(job)
        for job in state.get("google_jobs", []):
            job["source"] = "google"
            all_jobs.append(job)
        jobs_to_parse = all_jobs

    logger.info(f"Found {len(jobs_to_parse)} jobs to parse")

    if not jobs_to_parse:
        logger.warning("No jobs found to parse!")
        state["parsed_jobs"] = []
        return state

    # Process jobs in parallel batches with production-optimized settings
    parsed_jobs = await parallel_processor.process_jobs_in_batches(
        jobs=jobs_to_parse,
        processor_func=parse_single_job,
        batch_size=15,  # Much larger batches for CPU-bound parsing
        max_concurrent_batches=8  # Aggressive parallelization for parsing
    )

    # Calculate parsing statistics
    parsing_stats = {
        "total_jobs": len(jobs_to_parse),
        "jobs_with_salary": sum(1 for job in parsed_jobs if job.get("min_salary") or job.get("max_salary")),
        "jobs_with_skills": sum(1 for job in parsed_jobs if job.get("technical_skills")),
        "parsing_successes": sum(1 for job in parsed_jobs if job.get("parsing_success")),
        "parsing_timeouts": sum(1 for job in parsed_jobs if job.get("parsing_error") == "timeout"),
        "parsing_errors": sum(1 for job in parsed_jobs if job.get("parsing_error") and job.get("parsing_error") != "timeout")
    }

    # Calculate average skills per job
    total_skills = sum(len(job.get("technical_skills", [])) for job in parsed_jobs)
    parsing_stats["average_skills_per_job"] = round(total_skills / len(parsed_jobs), 1) if parsed_jobs else 0

    state["parsed_jobs"] = parsed_jobs
    state["parsing_stats"] = parsing_stats

    # Debug: Show what parsing produced
    if parsed_jobs:
        sample_job = parsed_jobs[0]
        print(f"🔍 DEBUG PARSING OUTPUT: First parsed job: {sample_job.get('title')} at {sample_job.get('company')}")
        logger.info(f"PARSING DEBUG: Sample parsed job:")
        logger.info(f"   Title: {sample_job.get('title', 'Unknown')}")
        logger.info(f"   Processing Status: {sample_job.get('processing_status', 'Unknown')}")
        logger.info(f"   Parsing Success: {sample_job.get('parsing_success', 'Unknown')}")

    logger.info(f"✅ Parallel parsing complete:")
    logger.info(f"   📊 Jobs processed: {parsing_stats['total_jobs']}")
    logger.info(f"   💰 Jobs with salary: {parsing_stats['jobs_with_salary']}")
    logger.info(f"   🛠️ Jobs with skills: {parsing_stats['jobs_with_skills']}")
    logger.info(f"   ✅ Parsing successes: {parsing_stats['parsing_successes']}")
    logger.info(f"   ⏱️ Parsing timeouts: {parsing_stats['parsing_timeouts']}")
    logger.info(f"   ❌ Parsing errors: {parsing_stats['parsing_errors']}")
    logger.info(f"   📈 Average skills per job: {parsing_stats['average_skills_per_job']}")

    return state
