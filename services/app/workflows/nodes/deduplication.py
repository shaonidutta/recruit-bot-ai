"""
Simple Job Deduplication Node
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def deduplication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate jobs by title + company"""
    logger.info("DEBUG: DEDUPLICATION NODE CALLED!")
    logger.info("Starting deduplication")
    logger.info(f"State keys in deduplication: {list(state.keys())}")

    # Try parsed jobs first (after parsing), then fallback to raw jobs (backward compatibility)
    jobs_to_deduplicate = state.get("parsed_jobs", []) or state.get("raw_jobs", [])
    logger.info(f"🔄 Jobs to deduplicate: {len(jobs_to_deduplicate)}")
    logger.info(f"🔄 Source: {'parsed_jobs' if state.get('parsed_jobs') else 'raw_jobs'}")

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
    logger.info(f"✅ Deduplicated: {len(jobs_to_deduplicate)} → {len(deduplicated)} jobs")

    return state


