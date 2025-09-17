"""
Simple Job Deduplication Node
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def deduplication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate jobs by title + company"""
    logger.info("Starting deduplication")

    # Try parsed jobs first (after parsing), then fallback to raw jobs (backward compatibility)
    jobs_to_deduplicate = state.get("parsed_jobs", []) or state.get("raw_jobs", [])

    print(f"🔍 DEBUG DEDUPLICATION: Available state keys: {list(state.keys())}")
    print(f"🔍 DEBUG DEDUPLICATION: Parsed jobs: {len(state.get('parsed_jobs', []))}")
    print(f"🔍 DEBUG DEDUPLICATION: Raw jobs: {len(state.get('raw_jobs', []))}")
    print(f"🔍 DEBUG DEDUPLICATION: Jobs to deduplicate: {len(jobs_to_deduplicate)}")

    if jobs_to_deduplicate:
        first_job = jobs_to_deduplicate[0]
        print(f"🔍 DEBUG DEDUPLICATION: First job: {first_job.get('title')} at {first_job.get('company')}")

    if not jobs_to_deduplicate:
        state["deduplicated_jobs"] = []
        return state

    # Simple deduplication by title + company
    seen = set()
    deduplicated = []

    for job in jobs_to_deduplicate:
        title = job.get("title", "").lower().strip()
        company = job.get("company", "").lower().strip()
        key = f"{title}|{company}"

        if key not in seen and title and company:
            seen.add(key)
            deduplicated.append(job)

    state["deduplicated_jobs"] = deduplicated

    if deduplicated:
        print(f"🔍 DEBUG DEDUPLICATION OUTPUT: First deduplicated job: {deduplicated[0].get('title')} at {deduplicated[0].get('company')}")

    logger.info(f"✅ Deduplicated: {len(jobs_to_deduplicate)} → {len(deduplicated)} jobs")

    return state


