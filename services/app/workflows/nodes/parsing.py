"""
Simple Rule-Based Job Parsing Node
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def parsing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parse job descriptions using simple rules"""
    logger.info("🔄 Starting parsing")

    enriched_jobs = state.get("enriched_jobs", [])
    if not enriched_jobs:
        state["parsed_jobs"] = []
        return state

    parsed_jobs = []

    for job in enriched_jobs:
        description = job.get("description", "").lower()
        title = job.get("title", "").lower()

        # Extract skills using keywords
        skills = _extract_skills(description + " " + title)

        # Extract experience level
        experience_level = _extract_experience_level(description + " " + title)

        # Extract salary range
        salary_range = _extract_salary(job.get("description", ""))

        # Add parsed data to job
        job["parsed_data"] = {
            "skills_required": skills,
            "experience_level": experience_level,
            "experience_years": _get_experience_years(experience_level),
            "requirements": _extract_requirements(description),
            "salary_range": salary_range
        }
        parsed_jobs.append(job)

    state["parsed_jobs"] = parsed_jobs
    logger.info(f"✅ Parsed {len(parsed_jobs)} jobs")

    return state

def _extract_skills(text: str) -> List[str]:
    """Extract skills using keyword matching"""
    skill_keywords = [
        "python", "javascript", "java", "react", "node.js", "sql", "mongodb",
        "aws", "docker", "kubernetes", "git", "html", "css", "typescript",
        "angular", "vue", "django", "flask", "spring", "postgresql", "mysql",
        "redis", "elasticsearch", "jenkins", "ci/cd", "agile", "scrum"
    ]

    found_skills = []
    for skill in skill_keywords:
        if skill in text:
            found_skills.append(skill.title())

    return found_skills

def _extract_experience_level(text: str) -> str:
    """Extract experience level"""
    if any(word in text for word in ["senior", "lead", "principal", "architect"]):
        return "Senior"
    elif any(word in text for word in ["junior", "entry", "graduate", "intern"]):
        return "Junior"
    else:
        return "Mid"

def _get_experience_years(level: str) -> int:
    """Convert experience level to years"""
    if level == "Senior":
        return 5
    elif level == "Junior":
        return 1
    else:
        return 3

def _extract_requirements(text: str) -> List[str]:
    """Extract basic requirements"""
    requirements = []
    if "degree" in text or "bachelor" in text:
        requirements.append("Bachelor's degree")
    if "experience" in text:
        requirements.append("Relevant experience")
    if "remote" in text:
        requirements.append("Remote work capability")
    return requirements

def _extract_salary(text: str) -> str | None:
    """Extract salary information"""
    # Look for salary patterns like $50,000, $50k, etc.
    salary_pattern = r'\$[\d,]+k?|\d+k\s*-\s*\d+k'
    match = re.search(salary_pattern, text, re.IGNORECASE)
    return match.group(0) if match else None
