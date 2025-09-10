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
            1. skills_categorized: Categorize technical skills into:
               - technical_skills: Programming languages (Python, Java, JavaScript, etc.)
               - frameworks: Web/app frameworks (Django, React, Angular, Flask, etc.)
               - databases: Database technologies (SQL, PostgreSQL, MongoDB, Redis, etc.)
               - cloud_platforms: Cloud services (AWS, Azure, GCP, Docker, Kubernetes, Terraform, etc.)
               - tools: Development tools (Git, Jenkins, etc.)
            2. experience_level: "entry", "mid", "senior", or "executive"
            3. experience_years: Number of years required (integer, null if not specified)
            4. requirements: List of key requirements/qualifications
            5. salary_range: Object with min_salary, max_salary, salary_type, currency (null if not mentioned)
            6. job_details: Object with job_type and remote_allowed:
               - job_type: "Full-Time", "Part-Time", "Contract", "Internship", etc.
               - remote_allowed: true if remote/hybrid work is mentioned, false otherwise
            7. benefits_mentioned: true if benefits are explicitly mentioned
            8. quality_score: Rate job description quality 1-10 (completeness, clarity)

            Return only valid JSON:
            {{
                "skills_categorized": {{
                    "technical_skills": ["Python", "JavaScript"],
                    "frameworks": ["Django", "React"],
                    "databases": ["SQL", "PostgreSQL"],
                    "cloud_platforms": ["AWS", "Docker"],
                    "tools": ["Git"]
                }},
                "experience_level": "mid",
                "experience_years": 3,
                "requirements": ["requirement1", "requirement2"],
                "salary_range": {{"min_salary": 80000, "max_salary": 120000, "salary_type": "annual", "currency": "USD"}} or null,
                "job_details": {{"job_type": "Full-Time", "remote_allowed": true}},
                "benefits_mentioned": true,
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
            llm_result = json.loads(response)

            # Transform LLM result to match expected structure
            skills_categorized = llm_result.get("skills_categorized", {})
            result = {
                "skills": {
                    "technical_skills": skills_categorized.get("technical_skills", []),
                    "frameworks": skills_categorized.get("frameworks", []),
                    "databases": skills_categorized.get("databases", []),
                    "cloud_platforms": skills_categorized.get("cloud_platforms", []),
                    "tools": skills_categorized.get("tools", []),
                    "methodologies": [],  # Could be enhanced
                    "soft_skills": []     # Could be enhanced
                },
                "experience": {
                    "level": llm_result.get("experience_level"),
                    "years": llm_result.get("experience_years")
                },
                "salary": self._convert_salary_to_int(llm_result.get("salary_range")),
                "requirements": llm_result.get("requirements", []),
                "job_details": llm_result.get("job_details", {}),
                "benefits_mentioned": llm_result.get("benefits_mentioned", False),
                "education": [],  # Could be enhanced
                "quality_score": llm_result.get("quality_score", 5),
                "processing_time": 0.5
            }

            return result

        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None

    def _convert_salary_to_int(self, salary_data):
        """Convert salary float values to integers for database storage"""
        if not salary_data or not isinstance(salary_data, dict):
            return salary_data

        converted = salary_data.copy()

        # Convert min_salary and max_salary to integers
        if 'min_salary' in converted and converted['min_salary'] is not None:
            try:
                converted['min_salary'] = int(float(converted['min_salary']))
            except (ValueError, TypeError):
                converted['min_salary'] = None

        if 'max_salary' in converted and converted['max_salary'] is not None:
            try:
                converted['max_salary'] = int(float(converted['max_salary']))
            except (ValueError, TypeError):
                converted['max_salary'] = None

        return converted

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
                "skills": skills,  # Now returns categorized skills dict
                "experience": experience,
                "salary": salary,  # Now returns salary dict with min/max
                "requirements": requirements,
                "education": self._extract_education(description),
                "quality_score": 5,  # Default quality score for regex parsing
                "processing_time": 0.1  # Simplified processing
            }

        except Exception as e:
            logger.error(f"Regex parsing failed: {e}")
            return self._empty_result()

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Enhanced skills extraction with categorization"""
        if not text:
            return {
                "technical_skills": [],
                "frameworks": [],
                "databases": [],
                "cloud_platforms": [],
                "tools": [],
                "methodologies": [],
                "soft_skills": []
            }

        text_lower = text.lower()

        # Enhanced skills dictionary with variations
        skills_dict = {
            "technical_skills": {
                "Python": ["python", "py"],
                "JavaScript": ["javascript", "js", "ecmascript"],
                "Java": ["java"],
                "C#": [".net", "dotnet", "dot net", "c#", "csharp"],
                "C++": ["c++", "cpp"],
                "TypeScript": ["typescript", "ts"],
                "PHP": ["php"],
                "Ruby": ["ruby"],
                "Go": ["golang", "go"],
                "Rust": ["rust"],
                "Swift": ["swift"],
                "Kotlin": ["kotlin"],
                "HTML": ["html", "html5"],
                "CSS": ["css", "css3"],
                "SQL": ["sql", "t-sql"]
            },
            "frameworks": {
                "React": ["react", "reactjs", "react.js"],
                "Angular": ["angular", "angularjs"],
                "Vue": ["vue", "vue.js", "vuejs"],
                "Node.js": ["node.js", "nodejs", "node"],
                "Express": ["express", "express.js"],
                "Django": ["django"],
                "Flask": ["flask"],
                "Spring": ["spring", "spring boot"],
                "ASP.NET": ["asp.net", "asp.net mvc", "asp.net core"],
                "Laravel": ["laravel"],
                "Rails": ["rails", "ruby on rails"],
                "Next.js": ["next.js", "nextjs"]
            },
            "databases": {
                "MySQL": ["mysql"],
                "PostgreSQL": ["postgresql", "postgres"],
                "MongoDB": ["mongodb", "mongo"],
                "Redis": ["redis"],
                "SQL Server": ["sql server", "mssql", "microsoft sql server"],
                "Oracle": ["oracle", "oracle db"],
                "SQLite": ["sqlite"]
            },
            "cloud_platforms": {
                "AWS": ["aws", "amazon web services"],
                "Azure": ["azure", "microsoft azure"],
                "GCP": ["gcp", "google cloud", "google cloud platform"],
                "Heroku": ["heroku"]
            },
            "tools": {
                "Git": ["git"],
                "Docker": ["docker"],
                "Kubernetes": ["kubernetes", "k8s"],
                "Jenkins": ["jenkins"],
                "Terraform": ["terraform"],
                "Visual Studio": ["visual studio", "vs code", "vscode"],
                "Jira": ["jira"],
                "Postman": ["postman"]
            },
            "methodologies": {
                "Agile": ["agile"],
                "Scrum": ["scrum"],
                "DevOps": ["devops", "dev ops"],
                "CI/CD": ["ci/cd", "continuous integration", "continuous deployment"],
                "REST API": ["rest", "rest api", "restful"],
                "Microservices": ["microservices", "micro services"]
            },
            "soft_skills": {
                "Communication": ["communication", "communicate"],
                "Leadership": ["leadership", "lead", "leading"],
                "Teamwork": ["teamwork", "team work", "collaboration"],
                "Problem Solving": ["problem solving", "problem-solving"],
                "Analytical": ["analytical", "analysis"]
            }
        }

        found_skills = {
            "technical_skills": [],
            "frameworks": [],
            "databases": [],
            "cloud_platforms": [],
            "tools": [],
            "methodologies": [],
            "soft_skills": []
        }

        # Extract skills by category
        for category, skills in skills_dict.items():
            for skill_name, variations in skills.items():
                for variation in variations:
                    if re.search(r'\b' + re.escape(variation) + r'\b', text_lower):
                        if skill_name not in found_skills[category]:
                            found_skills[category].append(skill_name)
                        break  # Found this skill, move to next

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

        # Extract years from description - focus on experience requirements
        text_lower = text.lower()

        # More specific patterns for job experience requirements
        experience_patterns = [
            r"minimum\s+of\s+(\d+)\+?\s*years?",
            r"at\s+least\s+(\d+)\+?\s*years?",
            r"(\d+)\+?\s*years?\s+of\s+experience",
            r"(\d+)\+?\s*years?\s+experience",
            r"(\d+)\+?\s*years?\s+in\s+",
            r"require[sd]?\s+(\d+)\+?\s*years?",
            r"minimum\s+(\d+)\+?\s*years?",
            r"(\d+)\+?\s*years?\s+(?:minimum|required|preferred)"
        ]

        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    years = int(matches[0])
                    # Filter out unrealistic values (company founding years, etc.)
                    if 1 <= years <= 20:  # Reasonable experience range
                        experience["years"] = years
                        break
                except (ValueError, IndexError):
                    continue

        # If no specific years found, infer from level
        if experience["years"] is None and experience["level"]:
            if experience["level"] == "senior":
                experience["years"] = 5
            elif experience["level"] == "junior":
                experience["years"] = 1
            else:
                experience["years"] = 3  # Default for mid-level

        return experience

    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Enhanced salary extraction with comprehensive patterns"""
        if not text:
            return None

        text_lower = text.lower()

        # Comprehensive salary patterns
        patterns = [
            # Annual salary ranges: "$92,000.00 Annually Up to: $115,000.00 Annually"
            r'(\$[\d,]+(?:\.\d{2})?)\s*annually\s*up\s*to:?\s*(\$[\d,]+(?:\.\d{2})?)\s*annually',
            r'minimum\s*starting\s*rate:?\s*(\$[\d,]+(?:\.\d{2})?)\s*annually\s*up\s*to:?\s*(\$[\d,]+(?:\.\d{2})?)\s*annually',

            # Standard ranges: "$80K - $120K", "$100,000 - $150,000"
            r'(\$[\d,]+[kK]?)\s*(?:to|-)\s*(\$[\d,]+[kK]?)',

            # Hourly rates: "$45-65/hour", "$50 per hour"
            r'(\$\d+(?:\.\d{2})?)\s*(?:to|-)\s*(\$\d+(?:\.\d{2})?)\s*(?:per\s*hour|/hour|hr)',

            # Single values with context
            r'salary:?\s*(\$[\d,]+[kK]?)',
            r'pay:?\s*(\$[\d,]+[kK]?)',
            r'compensation:?\s*(\$[\d,]+[kK]?)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                try:
                    match = matches[0]
                    if isinstance(match, tuple) and len(match) == 2:
                        # Range found
                        min_sal = self._parse_salary_amount(match[0])
                        max_sal = self._parse_salary_amount(match[1])

                        if min_sal and max_sal:
                            # Determine salary type - be more specific about hourly indicators
                            salary_type = "hourly" if any(term in text_lower for term in ["per hour", "/hour", "hourly", "/hr"]) else "annual"

                            # Override if we see clear annual indicators
                            if any(term in text_lower for term in ["annually", "per year", "yearly", "annual"]):
                                salary_type = "annual"

                            return {
                                "min_salary": int(min_sal) if min_sal else None,
                                "max_salary": int(max_sal) if max_sal else None,
                                "salary_type": salary_type,
                                "currency": "USD",
                                "equity_mentioned": "equity" in text_lower or "stock options" in text_lower,
                                "benefits_mentioned": "benefits" in text_lower or "comprehensive benefits" in text_lower,
                                "raw_salary_text": match[0] + " - " + match[1]
                            }
                    else:
                        # Single value
                        amount = self._parse_salary_amount(match if isinstance(match, str) else match[0])
                        if amount:
                            salary_type = "hourly" if any(term in text_lower for term in ["per hour", "/hour", "hourly", "/hr"]) else "annual"

                            # Override if we see clear annual indicators
                            if any(term in text_lower for term in ["annually", "per year", "yearly", "annual"]):
                                salary_type = "annual"

                            return {
                                "min_salary": int(amount) if amount else None,
                                "max_salary": int(amount) if amount else None,
                                "salary_type": salary_type,
                                "currency": "USD",
                                "equity_mentioned": "equity" in text_lower or "stock options" in text_lower,
                                "benefits_mentioned": "benefits" in text_lower or "comprehensive benefits" in text_lower,
                                "raw_salary_text": match if isinstance(match, str) else match[0]
                            }

                except (ValueError, AttributeError, IndexError):
                    continue

        return None

    def _parse_salary_amount(self, salary_str: str) -> Optional[int]:
        """Parse salary string to integer amount"""
        if not salary_str:
            return None

        try:
            # Remove $ and spaces
            clean_str = salary_str.replace('$', '').replace(',', '').replace(' ', '').lower()

            # Handle 'k' suffix
            if clean_str.endswith('k'):
                amount = float(clean_str[:-1]) * 1000
            else:
                amount = float(clean_str)

            return int(amount)

        except (ValueError, AttributeError):
            return None

    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements"""
        education_requirements = []
        text_lower = text.lower()

        if any(term in text_lower for term in ["bachelor", "bachelor's", "bs", "ba"]):
            education_requirements.append("Bachelor's degree")
        if any(term in text_lower for term in ["master", "master's", "ms", "ma", "mba"]):
            education_requirements.append("Master's degree")
        if any(term in text_lower for term in ["phd", "ph.d", "doctorate"]):
            education_requirements.append("PhD/Doctorate")
        if any(term in text_lower for term in ["associate", "associate's"]):
            education_requirements.append("Associate's degree")
        if any(term in text_lower for term in ["high school", "diploma", "ged"]):
            education_requirements.append("High school diploma")
        if any(term in text_lower for term in ["certification", "certified", "certificate"]):
            education_requirements.append("Professional certification")

        return education_requirements

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract general job requirements"""
        requirements = []
        text_lower = text.lower()

        # Work arrangement
        if "remote" in text_lower:
            requirements.append("Remote work capability")
        if "on-site" in text_lower or "onsite" in text_lower:
            requirements.append("On-site work required")
        if "hybrid" in text_lower:
            requirements.append("Hybrid work arrangement")

        # Experience requirements
        if "minimum" in text_lower and "years" in text_lower:
            requirements.append("Minimum experience requirement")
        if "senior" in text_lower or "lead" in text_lower:
            requirements.append("Senior-level position")
        if "entry" in text_lower or "junior" in text_lower:
            requirements.append("Entry-level position")

        # Communication and soft skills
        if any(term in text_lower for term in ["communication", "communicate"]):
            requirements.append("Strong communication skills")
        if any(term in text_lower for term in ["team", "collaboration", "collaborative"]):
            requirements.append("Team collaboration")
        if any(term in text_lower for term in ["leadership", "lead", "manage"]):
            requirements.append("Leadership experience")

        return requirements

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
