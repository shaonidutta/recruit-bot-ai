"""
LangSmith Integration for AI Recruitment Workflow Evaluation
Comprehensive tracing, evaluation, and monitoring system
"""

import os
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
import json
import asyncio
from functools import wraps
from dotenv import load_dotenv

# LangSmith imports
try:
    from langsmith import Client, traceable
    from langsmith.wrappers import wrap_openai
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    logging.warning("LangSmith not installed. Install with: pip install langsmith")

load_dotenv()
logger = logging.getLogger(__name__)

class LangSmithEvaluationService:
    """
    Complete LangSmith integration for workflow evaluation and monitoring
    Features:
    - Workflow step tracing
    - Email generation evaluation
    - Job matching quality assessment
    - Performance monitoring
    - A/B testing framework
    """
    
    def __init__(self):
        self.enabled = LANGSMITH_AVAILABLE and bool(os.getenv("LANGCHAIN_API_KEY"))
        
        if self.enabled:
            self.client = Client(
                api_url=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
                api_key=os.getenv("LANGCHAIN_API_KEY")
            )
            self.project_name = os.getenv("LANGCHAIN_PROJECT", "ai-recruitment-system")
            logger.info(f"✅ LangSmith enabled for project: {self.project_name}")
        else:
            logger.warning("⚠️ LangSmith disabled - missing API key or installation")
            self.client = None
    
    def trace_workflow_step(self, step_name: str, metadata: Optional[Dict] = None):
        """Decorator to trace individual workflow steps"""
        def decorator(func: Callable):
            if not self.enabled:
                return func

            # Use LangSmith's traceable decorator
            @traceable(
                name=step_name,
                project_name=self.project_name,
                metadata=metadata or {}
            )
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Execute the function
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Re-raise the exception to maintain error handling
                    logger.error(f"❌ {step_name} failed: {e}")
                    raise

            return wrapper
        return decorator
    
    async def evaluate_email_generation(
        self, 
        email_data: Dict[str, Any],
        job_details: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate generated email quality using LangSmith evaluators"""
        
        if not self.enabled:
            return {"evaluation_skipped": "LangSmith not enabled"}
        
        try:
            # Create evaluation dataset
            evaluation_data = {
                "input": {
                    "job_title": job_details.get("title"),
                    "company_name": company_info.get("name"),
                    "job_requirements": job_details.get("technical_skills", []),
                    "company_industry": company_info.get("industry")
                },
                "output": {
                    "subject": email_data.get("subject"),
                    "body": email_data.get("body_text"),
                    "personalization_elements": email_data.get("personalization_elements", [])
                }
            }
            
            # Define evaluation criteria
            evaluators = [
                self._create_personalization_evaluator(),
                self._create_professionalism_evaluator(),
                self._create_relevance_evaluator(),
                self._create_clarity_evaluator()
            ]
            
            # Run evaluations
            evaluation_results = {}
            for evaluator in evaluators:
                try:
                    result = await evaluator.evaluate(evaluation_data)
                    evaluation_results[evaluator.name] = result
                except Exception as e:
                    logger.warning(f"⚠️ Evaluator {evaluator.name} failed: {e}")
                    evaluation_results[evaluator.name] = {"error": str(e)}
            
            # Calculate overall email quality score
            overall_score = self._calculate_overall_email_score(evaluation_results)
            
            # Log evaluation to LangSmith
            if self.client:
                try:
                    self.client.create_run(
                        name="email_generation_evaluation",
                        run_type="chain",
                        inputs=evaluation_data["input"],
                        outputs=evaluation_data["output"],
                        extra={
                            "evaluation_results": evaluation_results,
                            "overall_score": overall_score,
                            "evaluated_at": datetime.now(timezone.utc).isoformat()
                        }
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to log to LangSmith: {e}")

            return {
                "overall_score": overall_score,
                "detailed_scores": evaluation_results,
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f" Email evaluation failed: {e}")
            return {"evaluation_error": str(e)}
    
    def _create_personalization_evaluator(self):
        """Create evaluator for email personalization quality"""
        return CustomEvaluator(
            name="personalization",
            criteria="Evaluate how well the email is personalized to the specific company and job role",
            scoring_rubric={
                "excellent": "Email includes specific company details, job requirements, and industry context",
                "good": "Email includes some company-specific details",
                "fair": "Email has minimal personalization",
                "poor": "Email appears generic with no personalization"
            }
        )
    
    def _create_professionalism_evaluator(self):
        """Create evaluator for email professionalism"""
        return CustomEvaluator(
            name="professionalism",
            criteria="Evaluate the professional tone, grammar, and business appropriateness",
            scoring_rubric={
                "excellent": "Perfect grammar, professional tone, appropriate business language",
                "good": "Minor grammar issues, mostly professional tone",
                "fair": "Some unprofessional elements or grammar errors",
                "poor": "Unprofessional tone or significant grammar issues"
            }
        )
    
    def _create_relevance_evaluator(self):
        """Create evaluator for content relevance"""
        return CustomEvaluator(
            name="relevance",
            criteria="Evaluate how relevant the email content is to recruitment and the specific role",
            scoring_rubric={
                "excellent": "Highly relevant to recruitment, specific role, and company needs",
                "good": "Mostly relevant with minor off-topic elements",
                "fair": "Somewhat relevant but lacks focus",
                "poor": "Not relevant to recruitment or the specific context"
            }
        )
    
    def _create_clarity_evaluator(self):
        """Create evaluator for message clarity and call-to-action"""
        return CustomEvaluator(
            name="clarity",
            criteria="Evaluate message clarity, structure, and effectiveness of call-to-action",
            scoring_rubric={
                "excellent": "Clear message, logical structure, compelling call-to-action",
                "good": "Mostly clear with minor structural issues",
                "fair": "Somewhat unclear or weak call-to-action",
                "poor": "Confusing message or no clear call-to-action"
            }
        )
    
    def _calculate_overall_email_score(self, evaluation_results: Dict[str, Any]) -> float:
        """Calculate overall email quality score from individual evaluations"""
        scores = []
        weights = {
            "personalization": 0.3,
            "professionalism": 0.25,
            "relevance": 0.25,
            "clarity": 0.2
        }
        
        for evaluator_name, result in evaluation_results.items():
            if isinstance(result, dict) and "score" in result:
                weight = weights.get(evaluator_name, 0.25)
                scores.append(result["score"] * weight)
        
        return sum(scores) if scores else 0.0
    
    async def evaluate_job_matching_quality(
        self,
        job_details: Dict[str, Any],
        candidate_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate the quality of job-candidate matching"""
        
        if not self.enabled:
            return {"evaluation_skipped": "LangSmith not enabled"}
        
        try:
            # Calculate matching metrics
            metrics = {
                "total_matches": len(candidate_matches),
                "avg_match_score": sum(m.get("score", 0) for m in candidate_matches) / len(candidate_matches) if candidate_matches else 0,
                "high_quality_matches": sum(1 for m in candidate_matches if m.get("score", 0) > 0.8),
                "skill_alignment_scores": [],
                "experience_alignment_scores": []
            }
            
            # Detailed skill alignment analysis
            job_skills = set(skill.lower() for skill in job_details.get("technical_skills", []))
            
            for match in candidate_matches:
                candidate_skills = set(skill.lower() for skill in match.get("skills", []))
                skill_overlap = len(job_skills.intersection(candidate_skills))
                skill_alignment = skill_overlap / len(job_skills) if job_skills else 0
                metrics["skill_alignment_scores"].append(skill_alignment)
            
            # Calculate overall matching quality
            overall_quality = self._calculate_matching_quality_score(metrics)
            
            # Log to LangSmith
            if self.client:
                try:
                    self.client.create_run(
                        name="job_matching_evaluation",
                        run_type="chain",
                        inputs={
                            "job_title": job_details.get("title"),
                            "required_skills": job_details.get("technical_skills", []),
                            "experience_required": job_details.get("experience_years_required")
                        },
                        outputs={
                            "matches_found": len(candidate_matches),
                            "quality_metrics": metrics
                        },
                        extra={
                            "overall_quality_score": overall_quality,
                            "evaluated_at": datetime.now(timezone.utc).isoformat()
                        }
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to log to LangSmith: {e}")

            return {
                "overall_quality_score": overall_quality,
                "detailed_metrics": metrics,
                "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Job matching evaluation failed: {e}")
            return {"evaluation_error": str(e)}
    
    def _calculate_matching_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall matching quality score"""
        score = 0.0
        
        # Base score from average match scores
        score += metrics["avg_match_score"] * 0.4
        
        # Bonus for having multiple high-quality matches
        if metrics["total_matches"] > 0:
            high_quality_ratio = metrics["high_quality_matches"] / metrics["total_matches"]
            score += high_quality_ratio * 0.3
        
        # Skill alignment bonus
        if metrics["skill_alignment_scores"]:
            avg_skill_alignment = sum(metrics["skill_alignment_scores"]) / len(metrics["skill_alignment_scores"])
            score += avg_skill_alignment * 0.3
        
        return min(score, 1.0)
    
    async def create_evaluation_dataset(
        self,
        dataset_name: str,
        examples: List[Dict[str, Any]]
    ) -> str:
        """Create evaluation dataset in LangSmith"""

        if not self.enabled or not self.client:
            logger.warning("⚠️ LangSmith not enabled or client not available - skipping dataset creation")
            return "dataset_creation_skipped"

        try:
            # Create dataset using LangSmith client
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=f"Evaluation dataset for AI recruitment system - {datetime.now(timezone.utc).isoformat()}"
            )

            # Add examples to dataset
            for example in examples:
                self.client.create_example(
                    dataset_id=dataset.id,
                    inputs=example.get("inputs", {}),
                    outputs=example.get("outputs", {}),
                    metadata=example.get("metadata", {})
                )

            logger.info(f"✅ Created evaluation dataset: {dataset_name} with {len(examples)} examples")
            return str(dataset.id)

        except Exception as e:
            logger.warning(f"⚠️ Failed to create evaluation dataset: {e}")
            return f"error: {str(e)}"
    
    async def run_workflow_evaluation(
        self,
        workflow_results: Dict[str, Any],
        evaluation_criteria: List[str]
    ) -> Dict[str, Any]:
        """Run comprehensive workflow evaluation"""
        
        if not self.enabled:
            return {"evaluation_skipped": "LangSmith not enabled"}
        
        evaluation_results = {
            "workflow_id": workflow_results.get("workflow_id"),
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
            "criteria_evaluated": evaluation_criteria,
            "scores": {},
            "recommendations": []
        }
        
        # Evaluate different aspects based on criteria
        for criterion in evaluation_criteria:
            try:
                if criterion == "email_quality":
                    # Evaluate email generation quality
                    email_results = workflow_results.get("outreach_results", {})
                    if email_results:
                        score = await self._evaluate_email_quality_from_results(email_results)
                        evaluation_results["scores"]["email_quality"] = score
                
                elif criterion == "matching_accuracy":
                    # Evaluate job matching accuracy
                    matches = workflow_results.get("matched_jobs", [])
                    if matches:
                        score = await self._evaluate_matching_accuracy(matches)
                        evaluation_results["scores"]["matching_accuracy"] = score
                
                elif criterion == "workflow_efficiency":
                    # Evaluate workflow execution efficiency
                    score = self._evaluate_workflow_efficiency(workflow_results)
                    evaluation_results["scores"]["workflow_efficiency"] = score
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to evaluate {criterion}: {e}")
                evaluation_results["scores"][criterion] = {"error": str(e)}
        
        # Generate recommendations
        evaluation_results["recommendations"] = self._generate_improvement_recommendations(
            evaluation_results["scores"]
        )
        
        return evaluation_results
    
    def _generate_improvement_recommendations(self, scores: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on evaluation scores"""
        recommendations = []
        
        for criterion, score in scores.items():
            if isinstance(score, (int, float)) and score < 0.7:
                if criterion == "email_quality":
                    recommendations.append("Consider improving email personalization and professional tone")
                elif criterion == "matching_accuracy":
                    recommendations.append("Review candidate matching algorithm parameters")
                elif criterion == "workflow_efficiency":
                    recommendations.append("Optimize workflow execution time and resource usage")
        
        return recommendations

    async def _evaluate_email_quality_from_results(self, email_results: Dict[str, Any]) -> float:
        """Evaluate email quality from workflow results"""
        try:
            # Extract email details from results
            email_details = email_results.get("email_details", [])
            if not email_details:
                return 0.0

            # Calculate average quality score based on available metrics
            total_score = 0.0
            for email in email_details:
                # Simple scoring based on available data
                score = 0.5  # Base score

                # Bonus for personalization elements
                if email.get("personalization_elements"):
                    score += 0.2

                # Bonus for successful sending
                if email.get("sent_successfully"):
                    score += 0.2

                # Bonus for LLM generation
                if email.get("llm_provider") == "gemini":
                    score += 0.1

                total_score += min(score, 1.0)

            return total_score / len(email_details)

        except Exception as e:
            logger.error(f"❌ Email quality evaluation failed: {e}")
            return 0.0

    async def _evaluate_matching_accuracy(self, matches: List[Dict[str, Any]]) -> float:
        """Evaluate matching accuracy from workflow results"""
        try:
            if not matches:
                return 0.0

            # Calculate average matching score
            total_score = 0.0
            for match in matches:
                # Get match score or calculate based on available data
                match_score = match.get("score", 0.5)

                # Bonus for having matched candidates
                if match.get("matches") or match.get("matched_candidates"):
                    match_score += 0.2

                total_score += min(match_score, 1.0)

            return total_score / len(matches)

        except Exception as e:
            logger.error(f"❌ Matching accuracy evaluation failed: {e}")
            return 0.0

    def _evaluate_workflow_efficiency(self, workflow_results: Dict[str, Any]) -> float:
        """Evaluate workflow execution efficiency"""
        try:
            # Base efficiency score
            efficiency_score = 0.5

            # Check execution time if available
            stats = workflow_results.get("stats", {})
            execution_time = stats.get("total_execution_time", 0)

            if execution_time > 0:
                # Good performance: < 10 seconds
                if execution_time < 10:
                    efficiency_score += 0.3
                # Acceptable: < 30 seconds
                elif execution_time < 30:
                    efficiency_score += 0.1
                # Poor: > 30 seconds
                else:
                    efficiency_score -= 0.1

            # Check success rate
            jobs_found = stats.get("jobs_found", 0)
            if jobs_found > 0:
                efficiency_score += 0.2

            return min(efficiency_score, 1.0)

        except Exception as e:
            logger.error(f"❌ Workflow efficiency evaluation failed: {e}")
            return 0.0

class CustomEvaluator:
    """Custom evaluator for specific evaluation criteria"""
    
    def __init__(self, name: str, criteria: str, scoring_rubric: Dict[str, str]):
        self.name = name
        self.criteria = criteria
        self.scoring_rubric = scoring_rubric
    
    async def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate data based on criteria (simplified implementation)"""
        # In production, this would use LLM-based evaluation
        # For now, return a simulated score based on data
        await asyncio.sleep(0.1)  # Simulate evaluation time

        # Simple scoring based on data availability
        score = 0.5  # Base score
        if data.get("subject"):
            score += 0.1
        if data.get("body_html"):
            score += 0.1
        if data.get("personalization_elements"):
            score += 0.2

        return {
            "score": min(score, 1.0),  # Cap at 1.0
            "reasoning": f"Evaluated based on {self.criteria} with data quality: {len(data)} fields",
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

# Global service instance
langsmith_service = LangSmithEvaluationService()
