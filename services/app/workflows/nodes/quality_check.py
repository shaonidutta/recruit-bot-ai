"""
Simple Quality Check Node (Rule-based)
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def quality_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Simple rule-based quality check"""
    logger.info("🔄 Starting quality check")

    parsed_jobs = state.get("parsed_jobs", [])
    print(f"🔍 DEBUG QUALITY CHECK: Available state keys: {list(state.keys())}")
    print(f"🔍 DEBUG QUALITY CHECK: Parsed jobs: {len(parsed_jobs)}")
    logger.info(f"🔍 DEBUG Quality check - Available state keys: {list(state.keys())}")
    logger.info(f"🔍 DEBUG Quality check - Parsed jobs: {len(parsed_jobs)}")

    if not parsed_jobs:
        state["quality_checked_jobs"] = []
        return state

    quality_checked_jobs = []

    for job in parsed_jobs:
        # Simple quality scoring based on completeness
        score = 0
        issues = []

        # Check required fields
        if job.get("title"):
            score += 2
        else:
            issues.append("Missing job title")

        if job.get("company"):
            score += 2
        else:
            issues.append("Missing company name")

        if job.get("description") and len(job.get("description", "")) > 100:
            score += 3
        else:
            issues.append("Description too short or missing")

        if job.get("location"):
            score += 1
        else:
            issues.append("Missing location")

        if job.get("url"):
            score += 1

        if job.get("salary_range"):
            score += 1

        # Set quality data
        job["quality_score"] = min(score, 10)  # Cap at 10
        job["quality_issues"] = issues
        job["is_high_quality"] = score >= 7

        quality_checked_jobs.append(job)

    state["quality_checked_jobs"] = quality_checked_jobs
    high_quality_count = sum(1 for job in quality_checked_jobs if job.get("is_high_quality", False))
    logger.info(f"✅ Quality checked {len(quality_checked_jobs)} jobs ({high_quality_count} high quality)")

    return state