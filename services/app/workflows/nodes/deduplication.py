"""
Simple Job Deduplication Node
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def deduplication_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Remove duplicate jobs by title + company"""
    logger.info("🔄 Starting deduplication")

    raw_jobs = state.get("raw_jobs", [])
    if not raw_jobs:
        state["deduplicated_jobs"] = []
        return state

    # Simple deduplication by title + company
    seen = set()
    deduplicated = []

    for job in raw_jobs:
        title = job.get("title", "").lower().strip()
        company = job.get("company", "").lower().strip()
        key = f"{title}|{company}"

        if key not in seen and title and company:
            seen.add(key)
            deduplicated.append(job)

    state["deduplicated_jobs"] = deduplicated
    logger.info(f"✅ Deduplicated: {len(raw_jobs)} → {len(deduplicated)} jobs")

    return state


