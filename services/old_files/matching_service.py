"""
Mid-Level Matching Service - Essential candidate-job matching
"""

import time
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Mid-level matching with skills + experience scoring"""

    def __init__(self):
        self.min_match_score = 0.7

    def match_candidates_to_job(self, job_data: Dict[str, Any], candidates: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
        """Score candidate matches for a job"""
        start_time = time.time()
        min_score = min_score or self.min_match_score

        if not candidates:
            return {"success": True, "matches": [], "processing_time": time.time() - start_time}

        # Extract job requirements
        job_skills = self._extract_job_skills(job_data.get("description", ""))
        job_experience = self._extract_experience_years(job_data.get("description", ""))

        matches = []
        for candidate in candidates:
            score = self._calculate_match_score(job_skills, job_experience, candidate)

            if score >= min_score:
                matches.append({
                    "candidate_id": candidate.get("id"),
                    "candidate_name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                    "overall_score": round(score, 2),
                    "skill_match": self._calculate_skill_overlap(job_skills, candidate.get("skills", [])),
                    "experience_match": self._calculate_experience_match(job_experience, candidate.get("experience_years"))
                })

        # Sort by score descending
        matches.sort(key=lambda x: x["overall_score"], reverse=True)

        return {
            "success": True,
            "matches": matches[:10],  # Top 10 matches
            "total_candidates": len(candidates),
            "qualified_matches": len(matches),
            "processing_time": time.time() - start_time
        }

    def _extract_job_skills(self, description: str) -> List[str]:
        """Extract skills from job description using simple keyword matching"""
        common_skills = [
            "python", "javascript", "java", "react", "node.js", "sql", "aws", "docker",
            "kubernetes", "git", "html", "css", "mongodb", "postgresql", "redis",
            "django", "flask", "express", "angular", "vue", "typescript", "go", "rust"
        ]

        description_lower = description.lower()
        found_skills = []

        for skill in common_skills:
            if skill in description_lower:
                found_skills.append(skill)

        return found_skills

    def _extract_experience_years(self, description: str) -> Optional[int]:
        """Extract required experience years from job description"""
        import re

        # Look for patterns like "3+ years", "5-7 years", etc.
        patterns = [
            r"(\d+)\+?\s*(?:to\s+(\d+))?\s*years?",
            r"(\d+)\+?\s*(?:to\s+(\d+))?\s*yrs?"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, description.lower())
            if matches:
                # Take the first number found
                return int(matches[0][0]) if matches[0][0] else None

        return None

    def _calculate_match_score(self, job_skills: List[str], job_experience: Optional[int], candidate: Dict[str, Any]) -> float:
        """Calculate overall match score (0-1)"""
        # Skills score (70% weight)
        skill_score = self._calculate_skill_overlap(job_skills, candidate.get("skills", []))

        # Experience score (30% weight)
        experience_score = self._calculate_experience_match(job_experience, candidate.get("experience_years"))

        # Weighted average
        overall_score = (skill_score * 0.7) + (experience_score * 0.3)

        return overall_score

    def _calculate_skill_overlap(self, job_skills: List[str], candidate_skills: List[str]) -> float:
        """Calculate skill overlap percentage"""
        if not job_skills:
            return 1.0

        job_skills_set = set(skill.lower() for skill in job_skills)
        candidate_skills_set = set(skill.lower() for skill in candidate_skills)

        overlap = len(job_skills_set.intersection(candidate_skills_set))
        return overlap / len(job_skills_set)

    def _calculate_experience_match(self, job_experience: Optional[int], candidate_experience: Optional[int]) -> float:
        """Calculate experience level match"""
        if job_experience is None or candidate_experience is None:
            return 0.8  # Neutral score when experience is unknown

        if candidate_experience >= job_experience:
            return 1.0  # Perfect match or overqualified
        else:
            # Partial score based on how close they are
            ratio = candidate_experience / job_experience
            return max(0.3, ratio)  # Minimum 30% score


# Global instance
matching_engine = MatchingEngine()

def get_matching_engine() -> MatchingEngine:
    """Get matching engine instance"""
    return matching_engine