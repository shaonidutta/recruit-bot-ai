"""
AI-Powered Matching Service - LLM-based semantic candidate-job matching
"""

import time
import json
from typing import Dict, List, Any, Optional
import logging

from ..config.llm_config import chat_completion, MODEL_CONFIGS

logger = logging.getLogger(__name__)


class MatchingEngine:
    """AI-powered matching with LLM-based semantic analysis"""

    def __init__(self):
        self.min_match_score = 0.7

    async def match_candidates_to_job(self, job_data: Dict[str, Any], candidates: List[Dict[str, Any]], min_score: Optional[float] = None) -> Dict[str, Any]:
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
            # Try LLM-powered matching first
            llm_match = await self._match_with_llm(job_data, candidate)
            if llm_match and llm_match["overall_score"] >= min_score:
                matches.append(llm_match)
            else:
                # Fallback to traditional scoring
                score = self._calculate_match_score(job_skills, job_experience, candidate)
                if score >= min_score:
                    matches.append({
                        "candidate_id": candidate.get("id"),
                        "candidate_name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                        "overall_score": round(score, 2),
                        "skill_match": self._calculate_skill_overlap(job_skills, candidate.get("skills", [])),
                        "experience_match": self._calculate_experience_match(job_experience, candidate.get("experience_years")),
                        "matching_method": "traditional"
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

    async def _match_with_llm(self, job_data: Dict[str, Any], candidate: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM for semantic matching between job and candidate"""
        try:
            job_title = job_data.get("title", "")
            job_description = job_data.get("description", "")
            job_skills = job_data.get("skills_required", [])

            candidate_name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
            candidate_skills = candidate.get("skills", [])
            candidate_experience = candidate.get("experience_years", 0)
            candidate_role = candidate.get("current_role", "")

            prompt = f"""
            Analyze the match between this job and candidate. Rate the match quality and provide detailed reasoning.

            JOB:
            Title: {job_title}
            Description: {job_description[:500]}...
            Required Skills: {job_skills}

            CANDIDATE:
            Name: {candidate_name}
            Current Role: {candidate_role}
            Experience: {candidate_experience} years
            Skills: {candidate_skills}

            Provide a JSON response with:
            1. overall_score: Float 0.0-1.0 (match quality)
            2. skill_match: Float 0.0-1.0 (skill alignment)
            3. experience_match: Float 0.0-1.0 (experience fit)
            4. reasoning: String (why this score)
            5. strengths: List of candidate strengths for this role
            6. gaps: List of areas where candidate may need development

            Return only valid JSON:
            {{
                "overall_score": 0.85,
                "skill_match": 0.9,
                "experience_match": 0.8,
                "reasoning": "Strong technical match with relevant experience",
                "strengths": ["Python expertise", "AWS experience"],
                "gaps": ["Limited React experience"]
            }}
            """

            messages = [
                {"role": "system", "content": "You are an expert technical recruiter. Analyze job-candidate matches objectively."},
                {"role": "user", "content": prompt}
            ]

            config = MODEL_CONFIGS["candidate_matching"]
            response = await chat_completion(
                messages=messages,
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )

            # Parse JSON response
            result = json.loads(response)

            # Add candidate info
            result.update({
                "candidate_id": candidate.get("id"),
                "candidate_name": candidate_name,
                "matching_method": "llm"
            })

            return result

        except Exception as e:
            logger.error(f"LLM matching failed: {e}")
            return None

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
