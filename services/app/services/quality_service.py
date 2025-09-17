"""
AI-Powered Quality Assessment Service
Determines if job data is good enough to proceed with matching
"""

import json
import logging
from typing import Dict, Any, Optional

from ..config.llm_config import chat_completion, MODEL_CONFIGS

logger = logging.getLogger(__name__)


class QualityAssessmentService:
    """LLM-based job data quality assessment"""

    def __init__(self):
        self.min_quality_score = 6  # Minimum score out of 10

    async def assess_job_quality(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess job data quality using LLM
        Returns quality score and recommendations
        """
        try:
            # Try LLM assessment first
            llm_result = await self._assess_with_llm(job_data)
            if llm_result:
                return llm_result
            
            # Fallback to rule-based assessment
            logger.warning("LLM quality assessment failed, falling back to rule-based")
            return self._assess_with_rules(job_data)

        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._default_assessment()

    async def _assess_with_llm(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to assess job data quality"""
        try:
            title = job_data.get("title", "")
            description = job_data.get("description", "")
            company = job_data.get("company", "")
            location = job_data.get("location", "")
            
            prompt = f"""
            Assess the quality of this job posting data. Rate how complete and useful it is for candidate matching.

            JOB DATA:
            Title: {title}
            Company: {company}
            Location: {location}
            Description: {description[:800]}...

            Evaluate based on:
            1. Title clarity and specificity
            2. Description completeness (skills, responsibilities, requirements)
            3. Company information availability
            4. Location specificity
            5. Overall usefulness for matching candidates

            Provide a JSON response:
            {{
                "quality_score": 8,
                "is_high_quality": true,
                "completeness": {{
                    "title": 9,
                    "description": 8,
                    "company": 7,
                    "location": 8
                }},
                "issues": ["Missing salary information", "Vague requirements"],
                "recommendations": ["Add specific skill requirements", "Include experience level"],
                "should_proceed": true
            }}

            Score 1-10 where:
            - 1-3: Very poor quality, missing critical information
            - 4-6: Moderate quality, some important details missing
            - 7-8: Good quality, minor improvements needed
            - 9-10: Excellent quality, comprehensive information
            """

            messages = [
                {"role": "system", "content": "You are an expert job posting quality assessor. Be objective and thorough."},
                {"role": "user", "content": prompt}
            ]

            config = MODEL_CONFIGS["enrichment"]  # Reuse enrichment config
            response = await chat_completion(
                messages=messages,
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"]
            )

            # Parse JSON response
            result = json.loads(response)
            
            # Add processing metadata
            result["assessment_method"] = "llm"
            result["should_proceed"] = result.get("quality_score", 0) >= self.min_quality_score
            
            return result

        except Exception as e:
            logger.error(f"LLM quality assessment failed: {e}")
            return None

    def _assess_with_rules(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based quality assessment"""
        title = job_data.get("title", "")
        description = job_data.get("description", "")
        company = job_data.get("company", "")
        location = job_data.get("location", "")
        
        # Simple scoring based on data presence and length
        title_score = 8 if title and len(title) > 5 else 3
        desc_score = 8 if description and len(description) > 100 else 4
        company_score = 7 if company and len(company) > 2 else 2
        location_score = 6 if location and len(location) > 3 else 2
        
        overall_score = (title_score + desc_score + company_score + location_score) / 4
        
        issues = []
        recommendations = []
        
        if not title or len(title) < 5:
            issues.append("Job title is missing or too short")
            recommendations.append("Add a clear, specific job title")
            
        if not description or len(description) < 100:
            issues.append("Job description is missing or too brief")
            recommendations.append("Add detailed job description with requirements")
            
        if not company:
            issues.append("Company name is missing")
            recommendations.append("Add company information")
            
        if not location:
            issues.append("Location information is missing")
            recommendations.append("Add job location details")

        return {
            "quality_score": round(overall_score, 1),
            "is_high_quality": overall_score >= 7,
            "completeness": {
                "title": title_score,
                "description": desc_score,
                "company": company_score,
                "location": location_score
            },
            "issues": issues,
            "recommendations": recommendations,
            "should_proceed": overall_score >= self.min_quality_score,
            "assessment_method": "rules"
        }

    def _default_assessment(self) -> Dict[str, Any]:
        """Default assessment when all methods fail"""
        return {
            "quality_score": 5,
            "is_high_quality": False,
            "completeness": {
                "title": 5,
                "description": 5,
                "company": 5,
                "location": 5
            },
            "issues": ["Quality assessment failed"],
            "recommendations": ["Manual review recommended"],
            "should_proceed": False,
            "assessment_method": "default"
        }


# Global instance
quality_service = QualityAssessmentService()

async def assess_job_quality(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main function for job quality assessment"""
    return await quality_service.assess_job_quality(job_data)
