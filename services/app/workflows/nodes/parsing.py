"""
Enhanced Job Parsing Node with Salary and Skills Extraction
"""

import logging
from typing import Dict, Any, List

from ...services.parsing_service import JobParsingService

logger = logging.getLogger(__name__)

# Initialize parsing service
parsing_service = JobParsingService()


async def parsing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse job descriptions to extract comprehensive skills, experience, and salary information"""
    logger.info("Starting enhanced parsing with salary and skills extraction")
    logger.info(f"DEBUG: State keys at parsing start: {list(state.keys())}")

    # Get jobs from the previous step (try multiple sources)
    jobs_to_parse = (
        state.get("enriched_jobs", []) or
        state.get("raw_jobs", []) or
        state.get("deduplicated_jobs", []) or
        []
    )

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

    logger.info(f"📋 Found {len(jobs_to_parse)} jobs to parse")
    logger.info(f"📋 State keys available: {list(state.keys())}")

    if not jobs_to_parse:
        logger.warning("⚠️ No jobs found to parse!")
        state["parsed_jobs"] = []
        return state

    parsed_jobs = []
    parsing_stats = {
        "total_jobs": len(jobs_to_parse),
        "jobs_with_salary": 0,
        "jobs_with_skills": 0,
        "average_skills_per_job": 0
    }

    for job in jobs_to_parse:
        try:
            description = job.get("description", "")
            title = job.get("title", "")

            if not description:
                logger.warning(f"⚠️ No description for job: {title}")
                parsed_jobs.append(job)
                continue

            # Use enhanced parsing service
            parsed_result = await parsing_service.parse_job_description(description, title)

            # Extract salary information
            salary_info = parsed_result.get("salary", {})
            if salary_info:
                job["min_salary"] = salary_info.get("min_salary")
                job["max_salary"] = salary_info.get("max_salary")
                job["salary_type"] = salary_info.get("salary_type", "annual")
                job["currency"] = salary_info.get("currency", "USD")
                job["equity_mentioned"] = salary_info.get("equity_mentioned", False)
                parsing_stats["jobs_with_salary"] += 1

            # Extract benefits information
            job["benefits_mentioned"] = parsed_result.get("benefits_mentioned", False)

            # Extract categorized skills
            skills_info = parsed_result.get("skills", {})
            if skills_info:
                job["technical_skills"] = skills_info.get("technical_skills", [])
                job["frameworks"] = skills_info.get("frameworks", [])
                job["databases"] = skills_info.get("databases", [])
                job["cloud_platforms"] = skills_info.get("cloud_platforms", [])
                job["tools"] = skills_info.get("tools", [])
                job["methodologies"] = skills_info.get("methodologies", [])
                job["soft_skills"] = skills_info.get("soft_skills", [])

                # Set skills_required for backward compatibility and matching
                all_skills = (
                    skills_info.get("technical_skills", []) +
                    skills_info.get("frameworks", []) +
                    skills_info.get("databases", []) +
                    skills_info.get("cloud_platforms", []) +
                    skills_info.get("tools", [])
                )
                job["skills_required"] = all_skills

                # Count total skills
                total_skills = sum(len(skills_list) for skills_list in skills_info.values())
                if total_skills > 0:
                    parsing_stats["jobs_with_skills"] += 1

            # Extract experience information
            experience_info = parsed_result.get("experience", {})
            if experience_info:
                job["experience_years_required"] = experience_info.get("years")
                job["experience_level"] = experience_info.get("level")

            # Extract education requirements
            education_info = parsed_result.get("education", [])
            if education_info:
                job["education_requirements"] = education_info

            # Extract job type and remote work info
            job_details = parsed_result.get("job_details", {})
            if job_details:
                job["job_type"] = job_details.get("job_type")
                job["remote_allowed"] = job_details.get("remote_allowed", False)

            # Set salary_range for backward compatibility
            if job.get("min_salary") and job.get("max_salary"):
                job["salary_range"] = f"${job.get('min_salary')}-${job.get('max_salary')}"

            # Set requirements at root level
            requirements = parsed_result.get("requirements", [])
            if requirements:
                job["requirements"] = requirements

            # Update processing status to indicate parsing is complete
            job["processing_status"] = "parsed"

            parsed_jobs.append(job)

        except Exception as e:
            logger.error(f"❌ Parsing failed for job {job.get('title', 'Unknown')}: {e}")
            # Add job without parsing data
            parsed_jobs.append(job)
            continue

    # Calculate parsing statistics
    if parsing_stats["jobs_with_skills"] > 0:
        total_skills = sum(
            len(job.get("technical_skills", [])) +
            len(job.get("frameworks", [])) +
            len(job.get("databases", [])) +
            len(job.get("cloud_platforms", [])) +
            len(job.get("tools", [])) +
            len(job.get("methodologies", [])) +
            len(job.get("soft_skills", []))
            for job in parsed_jobs
        )
        parsing_stats["average_skills_per_job"] = int(round(total_skills / len(parsed_jobs)))

    state["parsed_jobs"] = parsed_jobs
    state["parsing_stats"] = parsing_stats

    # Debug: Show what parsing produced
    if parsed_jobs:
        sample_job = parsed_jobs[0]
        logger.info(f"PARSING DEBUG: Sample parsed job:")
        logger.info(f"   Title: {sample_job.get('title', 'Unknown')}")
        logger.info(f"   Processing Status: {sample_job.get('processing_status', 'Unknown')}")
        logger.info(f"   Job Type: {sample_job.get('job_type', 'None')}")
        logger.info(f"   Requirements: {len(sample_job.get('requirements', []))} items")

    logger.info(f" Enhanced parsing complete:")
    logger.info(f"    Jobs processed: {parsing_stats['total_jobs']}")
    logger.info(f"    Jobs with salary: {parsing_stats['jobs_with_salary']}")
    logger.info(f"    Jobs with skills: {parsing_stats['jobs_with_skills']}")
    logger.info(f"    Average skills per job: {parsing_stats['average_skills_per_job']}")

    return state
