"""
Ultra-Simple Matching Node (Mock Matching)
"""

import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def matching_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock candidate matching for demo"""
    logger.info("🔄 Starting matching")

    quality_checked_jobs = state.get("quality_checked_jobs", state.get("parsed_jobs", []))
    if not quality_checked_jobs:
        state["matched_jobs"] = []
        return state

    # Mock candidates for demo
    mock_candidates = [
        {"id": "1", "name": "Rahul Sharma", "skills": ["Python", "React"], "experience": 3},
        {"id": "2", "name": "Priya Patel", "skills": ["Java", "Spring"], "experience": 5},
        {"id": "3", "name": "Amit Kumar", "skills": ["JavaScript", "Node.js"], "experience": 2},
        {"id": "4", "name": "Sneha Singh", "skills": ["Python", "Django"], "experience": 4},
        {"id": "5", "name": "Vikram Gupta", "skills": ["React", "TypeScript"], "experience": 6}
    ]

    matched_jobs = []

    for job in quality_checked_jobs:
        # Mock matching - randomly assign 1-3 candidates
        num_matches = random.randint(1, 3)
        selected_candidates = random.sample(mock_candidates, num_matches)

        matches = []
        for candidate in selected_candidates:
            matches.append({
                "candidate_id": candidate["id"],
                "candidate_name": candidate["name"],
                "score": round(random.uniform(0.7, 0.95), 2),
                "reasons": ["Skills match", "Experience level appropriate"]
            })

        job["matches"] = matches
        job["match_count"] = len(matches)
        matched_jobs.append(job)

    state["matched_jobs"] = matched_jobs
    total_matches = sum(job.get("match_count", 0) for job in matched_jobs)
    logger.info(f"✅ Matched {len(matched_jobs)} jobs with {total_matches} total matches")

    return state
