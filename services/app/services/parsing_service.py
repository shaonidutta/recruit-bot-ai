"""
AI-Powered Job Parsing Service - LLM-based skill and requirement extraction
"""

import re
import json
from typing import Dict, List, Any, Optional
import logging

from ..config.llm_config import chat_completion, MODEL_CONFIGS

logger = logging.getLogger(__name__)


class JobParsingService:
    """Mid-level job parsing with essential skill and experience extraction"""

    def __init__(self):
        # Core technical skills for matching
        self.core_skills = [
            "python", "javascript", "java", "react", "node.js", "sql", "aws", "docker",
            "kubernetes", "git", "html", "css", "mongodb", "postgresql", "redis",
            "django", "flask", "express", "angular", "vue", "typescript", "go", "rust",
            "c++", "c#", "php", "ruby", "swift", "kotlin", "scala", "terraform", "jenkins"
        ]

    async def parse_job_description(self, description: str, job_title: str = "") -> Dict[str, Any]:
        """Parse job description and extract key information using LLM"""
        if not description:
            return self._empty_result()

        try:
            # Try LLM-powered parsing first
            llm_result = await self._parse_with_llm(description, job_title)
            if llm_result:
                return llm_result

            # Fallback to regex-based parsing
            logger.warning("LLM parsing failed, falling back to regex parsing")
            return self._parse_with_regex(description, job_title)

        except Exception as e:
            logger.error(f"Job parsing failed: {e}")
            return self._empty_result()

    async def _parse_with_llm(self, description: str, job_title: str = "") -> Optional[Dict[str, Any]]:
        """Parse job description using LLM"""
        try:
            prompt = f"""
            Analyze this job description and extract the following information in JSON format:

            Job Title: {job_title}
            Job Description: {description}

            Extract:
            1. skills_required: List of technical skills mentioned (programming languages, frameworks, tools)
            2. experience_level: "entry", "mid", "senior", or "executive"
            3. experience_years: Number of years required (integer, null if not specified)
            4. requirements: List of key requirements/qualifications
            5. salary_range: Object with min, max, currency (null if not mentioned)
            6. quality_score: Rate job description quality 1-10 (completeness, clarity)

            Return only valid JSON:
            {{
                "skills_required": ["skill1", "skill2"],
                "experience_level": "mid",
                "experience_years": 3,
                "requirements": ["requirement1", "requirement2"],
                "salary_range": {{"min": 80000, "max": 120000, "currency": "USD"}} or null,
                "quality_score": 8
            }}
            """

            messages = [
                {"role": "system", "content": "You are an expert job description analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]

            config = MODEL_CONFIGS["job_parsing"]
            response = await chat_completion(
                messages=messages,
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )

            # Parse JSON response
            result = json.loads(response)
            result["processing_time"] = 0.5  # LLM processing time
            return result

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None

    def _parse_with_regex(self, description: str, job_title: str = "") -> Dict[str, Any]:
        """Fallback regex-based parsing"""
        try:
            # Extract skills
            skills = self._extract_skills(description)

            # Extract experience requirements
            experience = self._extract_experience(description, job_title)

            # Extract salary information
            salary = self._extract_salary(description)

            # Extract basic requirements
            requirements = self._extract_requirements(description)

            return {
                "skills_required": list(skills),
                "experience_level": experience.get("level"),
                "experience_years": experience.get("years"),
                "requirements": requirements,
                "salary_range": salary,
                "quality_score": 5,  # Default quality score for regex parsing
                "processing_time": 0.1  # Simplified processing
            }

        except Exception as e:
            logger.error(f"Regex parsing failed: {e}")
            return self._empty_result()

    def _extract_skills(self, text: str) -> set:
        """Extract technical skills from job description"""
        text_lower = text.lower()
        found_skills = set()

        for skill in self.core_skills:
            # Simple keyword matching with word boundaries
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found_skills.add(skill)

        return found_skills

    def _extract_experience(self, text: str, job_title: str = "") -> Dict[str, Any]:
        """Extract experience level and years"""
        experience: Dict[str, Any] = {"level": None, "years": None}

        # Check job title for level indicators
        title_lower = job_title.lower()
        if any(word in title_lower for word in ["senior", "sr", "lead", "principal"]):
            experience["level"] = "senior"
        elif any(word in title_lower for word in ["junior", "jr", "entry", "graduate"]):
            experience["level"] = "junior"

        # Extract years from description
        year_patterns = [
            r"(\d+)\+?\s*(?:to\s+(\d+))?\s*years?",
            r"(\d+)\+?\s*(?:to\s+(\d+))?\s*yrs?"
        ]

        for pattern in year_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    experience["years"] = int(matches[0][0])
                    break
                except (ValueError, IndexError):
                    continue

        return experience

    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract salary information"""
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand)?',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:k|thousand)',
            r'salary.*?(\d{1,3}(?:,\d{3})*)'
        ]

        for pattern in salary_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    amount = int(matches[0].replace(',', ''))
                    # Convert k to thousands
                    if 'k' in text.lower() and amount < 1000:
                        amount *= 1000

                    return {
                        "min": amount,
                        "max": amount,
                        "currency": "USD"
                    }
                except (ValueError, AttributeError):
                    continue

        return None

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract basic requirements from job description"""
        requirements = []

        # Look for common requirement indicators
        requirement_patterns = [
            r'(?:requirements?|qualifications?|must have)[:\s]*([^.!?]*)',
            r'(?:required|essential)[:\s]*([^.!?]*)',
            r'(?:you should have|you must have)[:\s]*([^.!?]*)'
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if match.strip():
                    requirements.append(match.strip())

        return requirements[:5]  # Limit to top 5 requirements

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty parsing result"""
        return {
            "skills_required": [],
            "experience_level": None,
            "experience_years": None,
            "requirements": [],
            "salary_range": None,
            "quality_score": 1,  # Low quality for empty results
            "processing_time": 0
        }


# Global instance
parsing_service = JobParsingService()

async def parse_job_description(description: str, job_title: str = "") -> Dict[str, Any]:
    """Main function for parsing job descriptions"""
    return await parsing_service.parse_job_description(description, job_title)
