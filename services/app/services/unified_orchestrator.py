"""
Unified LangGraph Orchestrator
Complete recruitment pipeline: Scraping → Processing → Matching → Storage
Replaces both agent_orchestrator.py and base_workflow.py
"""
import os
import logging
import asyncio

from typing import Dict, List, Any, TypedDict, Annotated
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END
from operator import add

# Custom reducer for keywords (last value wins)
def keywords_reducer(x: str, y: str) -> str:
    return y if y else x

# Import agents
from ..agents.linkedin_agent import fetch_linkedin_jobs
from ..agents.indeed_agent import fetch_indeed_jobs
from ..agents.google_agent import fetch_google_jobs

# Import workflow nodes
from ..workflows.nodes.deduplication import deduplication_node
from ..workflows.nodes.enrichment import enrichment_node
from ..workflows.nodes.parsing import parsing_node
from ..workflows.nodes.quality_check import quality_check_node
from ..workflows.nodes.matching import matching_node
from ..workflows.nodes.storage import storage_node
from .outreach_email_service import send_professional_outreach_email, send_sync_email  # NEW IMPORT

from ..config.constants import DEFAULT_KEYWORDS

logger = logging.getLogger(__name__)

class UnifiedRecruitmentState(TypedDict):
    """Complete state schema for the unified recruitment workflow"""
    # Input - use Annotated to allow concurrent access
    keywords: Annotated[str, keywords_reducer]  # Allow concurrent access

    # Scraping results (parallel) - each modified by single node
    linkedin_jobs: List[Dict[str, Any]]
    indeed_jobs: List[Dict[str, Any]]
    google_jobs: List[Dict[str, Any]]

    # Processing stages (sequential)
    raw_jobs: List[Dict[str, Any]]
    deduplicated_jobs: List[Dict[str, Any]]
    enriched_jobs: List[Dict[str, Any]]
    parsed_jobs: List[Dict[str, Any]]
    quality_checked_jobs: List[Dict[str, Any]]
    matched_jobs: List[Dict[str, Any]]
    outreach_results: Dict[str, Any]  # Email outreach results
    stored_jobs: List[Dict[str, Any]]

    # Workflow metadata
    workflow_id: str
    current_step: str
    started_at: str
    completed_at: str
    errors: Annotated[List[str], add]  # Allow concurrent updates
    stats: Dict[str, Any]
    config: Dict[str, Any]

class UnifiedOrchestrator:
    """Unified LangGraph orchestrator for complete recruitment pipeline"""
    
    def __init__(self):
        self.graph = self._build_unified_graph()
    
    def _build_unified_graph(self):
        """Build the complete unified LangGraph workflow"""
        workflow = StateGraph(UnifiedRecruitmentState)
        
        # Add initialization node
        workflow.add_node("init", self._init_node)

        # Add scraping nodes (parallel execution)
        workflow.add_node("linkedin_scraper", self._linkedin_node)
        workflow.add_node("indeed_scraper", self._indeed_node)
        workflow.add_node("google_scraper", self._google_node)

        # Add aggregation node
        workflow.add_node("aggregate", self._aggregate_node)

        # Add processing nodes (sequential execution)
        workflow.add_node("deduplicate", self._deduplication_wrapper)
        workflow.add_node("enrich", self._enrichment_wrapper)
        workflow.add_node("parse", self._parsing_wrapper)
        workflow.add_node("quality_check", self._quality_wrapper)
        workflow.add_node("match", self._matching_wrapper)
        workflow.add_node("outreach", self._outreach_wrapper)  # NEW: Email outreach node
        workflow.add_node("store", self._storage_wrapper)

        # Set single entry point
        workflow.set_entry_point("init")

        # Connect scrapers sequentially to avoid concurrent state access
        workflow.add_edge("init", "linkedin_scraper")
        workflow.add_edge("linkedin_scraper", "indeed_scraper")
        workflow.add_edge("indeed_scraper", "google_scraper")
        workflow.add_edge("google_scraper", "aggregate")
        
        # Sequential processing pipeline - CORRECTED ORDER
        workflow.add_edge("aggregate", "parse")        # Parse job descriptions first
        workflow.add_edge("parse", "deduplicate")      # Then deduplicate parsed jobs
        workflow.add_edge("deduplicate", "enrich")     # Then enrich with company data
        workflow.add_edge("enrich", "quality_check")   # Quality check enriched jobs
        workflow.add_edge("quality_check", "match")    # Match with candidates
        workflow.add_edge("match", "outreach")         # Send outreach emails
        workflow.add_edge("outreach", "store")         # Store everything
        workflow.add_edge("store", END)
        
        return workflow.compile()

    async def _run_workflow_with_retry(self, initial_state: UnifiedRecruitmentState, max_retries: int = 2) -> UnifiedRecruitmentState:
        """Run workflow with retry logic for critical failures"""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Workflow attempt {attempt + 1}/{max_retries + 1}")
                logger.info(f"DEBUG: About to invoke graph with state keys: {list(initial_state.keys())}")

                # Run the workflow
                logger.info("DEBUG: About to invoke LangGraph")
                final_state = await self.graph.ainvoke(initial_state)
                logger.info("DEBUG: LangGraph execution completed")

                logger.info(f"DEBUG: Graph execution completed. Final state keys: {list(final_state.keys())}")

                # Check for critical failures
                errors = final_state.get("errors", [])
                critical_errors = [err for err in errors if any(critical in err.lower() for critical in
                                 ["database", "connection", "timeout", "authentication"])]

                if critical_errors and attempt < max_retries:
                    logger.warning(f"Critical errors detected, retrying: {critical_errors}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue

                # Success or final attempt
                if attempt > 0:
                    logger.info(f"Workflow succeeded on attempt {attempt + 1}")

                return final_state  # type: ignore

            except Exception as e:
                last_error = e
                logger.error(f"Workflow attempt {attempt + 1} failed: {e}")

                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All workflow attempts failed. Last error: {e}")
                    # Return a minimal state with error information
                    error_state = dict(initial_state)
                    error_state["errors"] = initial_state.get("errors", []) + [f"Workflow failed: {str(e)}"]
                    error_state["completed_at"] = datetime.now(timezone.utc).isoformat()
                    return error_state  # type: ignore

        # This should never be reached, but just in case
        raise last_error or Exception("Unknown workflow error")

    async def _run_node_with_error_handling(self, node_name: str, node_func, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Run a workflow node with comprehensive error handling"""
        try:
            print(f"🔧 DEBUG: About to run {node_name} node")
            logger.info(f"Starting {node_name}")
            logger.info(f"🔧 DEBUG: About to run {node_name} node")
            start_time = datetime.now()

            # Run the node
            print(f"🔧 DEBUG: Calling {node_name} function: {node_func}")
            logger.info(f"🔧 DEBUG: Calling {node_name} function: {node_func}")
            result = await node_func(dict(state))
            print(f"🔧 DEBUG: {node_name} function returned: {type(result)}")
            logger.info(f"🔧 DEBUG: {node_name} function returned: {type(result)}")

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{node_name} completed in {processing_time:.2f}s")

            # Update state with results
            for key, value in result.items():
                if key in state:
                    state[key] = value

            return state

        except Exception as e:
            print(f"🚨 ERROR in {node_name}: {e}")
            logger.error(f"{node_name} failed: {e}")
            logger.error(f"🚨 FULL ERROR TRACEBACK for {node_name}:", exc_info=True)

            # Add error to state
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"{node_name}: {str(e)}")

            # For critical nodes, we might want to stop the workflow
            critical_nodes = ["storage", "database"]
            if any(critical in node_name.lower() for critical in critical_nodes):
                logger.error(f"🚨 Critical node {node_name} failed, workflow may be compromised")

            return state

    # Initialization Node
    async def _init_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Initialize the workflow state"""
        logger.info("Starting unified recruitment workflow")
        logger.info(f"Keywords: {state['keywords']}")
        return state

    # Scraping Nodes (Parallel) with Enhanced Error Handling
    async def _linkedin_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """LinkedIn scraping agent with enhanced error handling"""
        try:
            logger.info("🔍 Running LinkedIn agent...")
            start_time = datetime.now()

            jobs = await fetch_linkedin_jobs(state["keywords"])

            processing_time = (datetime.now() - start_time).total_seconds()
            state["linkedin_jobs"] = jobs
            logger.info(f"LinkedIn: {len(jobs)} jobs found in {processing_time:.2f}s")

        except Exception as e:
            logger.error(f"LinkedIn agent failed: {e}")
            state["linkedin_jobs"] = []
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"LinkedIn scraping: {str(e)}")
        return state
    
    async def _indeed_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Indeed scraping agent with enhanced error handling"""
        try:
            logger.info("🔍 Running Indeed agent...")
            start_time = datetime.now()

            jobs = await fetch_indeed_jobs(state["keywords"])

            processing_time = (datetime.now() - start_time).total_seconds()
            state["indeed_jobs"] = jobs
            logger.info(f"Indeed: {len(jobs)} jobs found in {processing_time:.2f}s")

        except Exception as e:
            logger.error(f"Indeed agent failed: {e}")
            state["indeed_jobs"] = []
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Indeed scraping: {str(e)}")
        return state
    
    async def _google_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Google Jobs scraping agent with enhanced error handling"""
        try:
            logger.info("🔍 Running Google agent...")
            start_time = datetime.now()

            jobs = await fetch_google_jobs(state["keywords"])

            processing_time = (datetime.now() - start_time).total_seconds()
            state["google_jobs"] = jobs
            logger.info(f"Google: {len(jobs)} jobs found in {processing_time:.2f}s")

        except Exception as e:
            logger.error(f"Google agent failed: {e}")
            state["google_jobs"] = []
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Google scraping: {str(e)}")
        return state
    
    # Aggregation Node
    async def _aggregate_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Aggregate all scraping results"""
        try:
            logger.info("DEBUG: AGGREGATE NODE CALLED!")
            logger.info("Aggregating scraping results...")
            logger.info(f"State keys before aggregation: {list(state.keys())}")

            # Combine all jobs
            all_jobs = []
            
            # Add source metadata
            for job in state.get("linkedin_jobs", []):
                job["source"] = "linkedin"
                all_jobs.append(job)
            
            for job in state.get("indeed_jobs", []):
                job["source"] = "indeed"
                all_jobs.append(job)
                
            for job in state.get("google_jobs", []):
                job["source"] = "google"
                all_jobs.append(job)
            
            state["raw_jobs"] = all_jobs
            
            # Initialize stats
            state["stats"] = {
                "total_jobs_discovered": len(all_jobs),
                "linkedin_jobs": len(state.get("linkedin_jobs", [])),
                "indeed_jobs": len(state.get("indeed_jobs", [])),
                "google_jobs": len(state.get("google_jobs", [])),
                "processing_time_seconds": 0
            }
            
            logger.info(f"Aggregated {len(all_jobs)} total jobs")

        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            state["raw_jobs"] = []
            state["errors"].append(f"Aggregation: {str(e)}")
        
        return state

    # Email Outreach Node
    async def _outreach_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Send outreach emails to hiring managers for matched jobs"""
        try:
            logger.info("Starting email outreach...")

            # Get matched jobs from state
            matched_jobs = state.get("matched_jobs", [])
            if not matched_jobs:
                logger.info("No matched jobs for outreach")
                state["outreach_results"] = {"emails_sent": 0, "emails_failed": 0}
                return state

            # Skip contacts loading - using direct email configuration
            # Contacts functionality kept in code but not used in workflow
            demo_contact = {"email": "abhijeet.kr.chaurasiya@gmail.com", "name": "Demo Contact"}
            emails_sent = 0
            emails_failed = 0

            # Send outreach email for each matched job (limit to 3 for demo)
            for job in matched_jobs[:3]:  # Limit to first 3 jobs for demo
                try:
                    # Get job details
                    job_title = job.get("title", "Position")
                    company_name = job.get("company", "Company")

                    # Get matched candidates for this job
                    candidates = job.get("matched_candidates", [])
                    if not candidates:
                        continue

                    # Send professional outreach email
                    result = await send_professional_outreach_email(
                        recruiter_email=demo_contact["email"],
                        job_title=job_title,
                        company_name=company_name,
                        company_achievement="Growing tech company",  # Demo data
                        candidates=candidates[:2],  # Top 2 candidates
                        subject=f"Top Candidates for {job_title} Position"
                    )

                    if result.get("success", False):
                        emails_sent += 1
                        logger.info(f"Outreach email sent for {job_title} at {company_name}")
                    else:
                        emails_failed += 1
                        logger.error(f"Failed to send outreach email for {job_title}")

                except Exception as e:
                    emails_failed += 1
                    logger.error(f"Error sending outreach email: {e}")

            # Store results
            state["outreach_results"] = {
                "emails_sent": emails_sent,
                "emails_failed": emails_failed,
                "contact_used": demo_contact["email"],
                "jobs_processed": len(matched_jobs[:3])
            }

            logger.info(f"Outreach completed: {emails_sent} sent, {emails_failed} failed")

        except Exception as e:
            logger.error(f"Outreach node failed: {e}")
            state["outreach_results"] = {"emails_sent": 0, "emails_failed": 0, "error": str(e)}
            state["errors"].append(f"Outreach: {str(e)}")

        return state

    # Processing Node Wrappers (Sequential) with Enhanced Error Handling
    async def _deduplication_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for deduplication node with error handling"""
        return await self._run_node_with_error_handling("Deduplication", deduplication_node, state)

    async def _enrichment_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for enrichment node with error handling"""
        return await self._run_node_with_error_handling("Enrichment", enrichment_node, state)

    async def _parsing_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for parsing node with error handling"""
        logger.info("DEBUG: PARSING WRAPPER CALLED!")
        logger.info(f"State keys in parsing wrapper: {list(state.keys())}")
        logger.info(f"Raw jobs count: {len(state.get('raw_jobs', []))}")
        return await self._run_node_with_error_handling("Parsing", parsing_node, state)

    async def _quality_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for quality check node with error handling"""
        logger.info("🚨 QUALITY CHECK WRAPPER CALLED - DEBUG")
        logger.info(f"🔍 State keys in quality wrapper: {list(state.keys())}")
        result = await self._run_node_with_error_handling("Quality Check", quality_check_node, state)
        logger.info("🚨 QUALITY CHECK WRAPPER COMPLETED - DEBUG")
        return result

    async def _matching_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for matching node with error handling"""
        print("🚨 MATCHING WRAPPER CALLED - DEBUG")
        logger.info("🚨 MATCHING WRAPPER CALLED - DEBUG")
        logger.info(f"🔍 State keys in matching wrapper: {list(state.keys())}")
        print(f"🔍 State keys in matching wrapper: {list(state.keys())}")

        # DEBUG: Check quality_checked_jobs data
        quality_jobs = state.get('quality_checked_jobs', [])
        print(f"🔍 Quality checked jobs count: {len(quality_jobs)}")
        logger.info(f"🔍 Quality checked jobs count: {len(quality_jobs)}")
        if quality_jobs:
            print(f"🔍 First quality job: {quality_jobs[0].get('title', 'No title')}")
            logger.info(f"🔍 First quality job: {quality_jobs[0].get('title', 'No title')}")

        result = await self._run_node_with_error_handling("Matching", matching_node, state)
        print("🚨 MATCHING WRAPPER COMPLETED - DEBUG")
        logger.info("🚨 MATCHING WRAPPER COMPLETED - DEBUG")
        return result

    async def _outreach_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for email outreach node"""
        logger.info("Step 7: Email Outreach")
        result = await self._outreach_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state

    async def _storage_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for storage node with error handling"""
        print("🚨 STORAGE WRAPPER CALLED - DEBUG")
        logger.info("🚨 STORAGE WRAPPER CALLED - DEBUG")
        result = await self._run_node_with_error_handling("Storage", storage_node, state)
        print("🚨 STORAGE WRAPPER COMPLETED - DEBUG")
        logger.info("🚨 STORAGE WRAPPER COMPLETED - DEBUG")
        return result
    
    def _get_candidate_title(self, match: dict) -> str:
        """Generate professional title for candidate based on match data"""
        candidate_name = match.get("candidate_name", "")
        if "senior" in candidate_name.lower() or match.get("score", 0) > 0.9:
            return "Senior Developer"
        elif "lead" in candidate_name.lower():
            return "Lead Developer"
        else:
            return "Software Engineer"
    
    def _get_candidate_expertise(self, match: dict, job: dict) -> str:
        """Generate expertise description for candidate"""
        candidate_name = match.get("candidate_name", "")
        job_title = job.get("title", "")
        
        # Extract key technologies from job title/description
        technologies = []
        if "react" in job_title.lower():
            technologies.append("React.js")
        if "typescript" in job_title.lower():
            technologies.append("TypeScript")
        if "python" in job_title.lower():
            technologies.append("Python")
        if "node" in job_title.lower():
            technologies.append("Node.js")
        
        if not technologies:
            technologies = ["modern web technologies", "full-stack development"]
        
        years = "6+" if "senior" in candidate_name.lower() else "5+" if "lead" in candidate_name.lower() else "4+"
        tech_list = ", ".join(technologies[:3])  # Limit to 3 technologies
        
        return f"{years} years specializing in {tech_list}. Recently led successful projects involving scalable architecture and performance optimization, resulting in significant improvements in system efficiency."
    
    def _get_why_candidate_fits(self, match: dict, job: dict) -> str:
        """Generate why candidate fits description"""
        score = match.get("score", 0)
        job_title = job.get("title", "")
        
        if score > 0.9:
            return f"Exceptional alignment with your technical requirements and proven track record in similar roles. Their expertise directly matches the challenges outlined in your {job_title} position."
        elif score > 0.8:
            return f"Strong technical alignment with hands-on experience that directly addresses the key requirements for your {job_title} role."
        else:
            return f"Solid technical foundation with relevant experience that aligns well with your {job_title} position requirements."
    
    def _get_company_achievement(self, company: str) -> str:
        """Generate company achievement based on company name"""
        # Mock achievements for demo - in real implementation, this would query a database
        achievements = {
            "innovatetech": "the recent launch of FutureDesk",
            "techcorp": "your successful Series B funding round",
            "websolutions": "the launch of your new AI-powered platform",
            "default": "your recent product innovations and market expansion"
        }
        
        company_key = company.lower().replace(" ", "").replace("inc", "").replace("llc", "")
        return achievements.get(company_key, achievements["default"])
    
    # Main execution method
    async def run_complete_workflow(self, keywords: str = "Software Engineer") -> Dict[str, Any]:
        """Run the complete recruitment workflow"""
        try:
            # Ensure database connection is established
            from ..config.database import connect_to_mongo
            await connect_to_mongo()
            logger.info("✅ Database connection established for workflow")

            # Track start time and generate workflow ID
            start_time = datetime.now(timezone.utc)
            workflow_id = f"unified_{start_time.strftime('%Y%m%d_%H%M%S')}"

            # Initialize state
            initial_state: UnifiedRecruitmentState = {
                "keywords": keywords or DEFAULT_KEYWORDS,
                "linkedin_jobs": [],
                "indeed_jobs": [],
                "google_jobs": [],
                "raw_jobs": [],
                "deduplicated_jobs": [],
                "enriched_jobs": [],
                "parsed_jobs": [],
                "quality_checked_jobs": [],
                "matched_jobs": [],
                "outreach_results": {},
                "stored_jobs": [],
                "workflow_id": workflow_id,
                "current_step": "starting",
                "started_at": start_time.isoformat(),
                "completed_at": "",
                "errors": [],
                "stats": {},
                "config": {
                    "max_concurrent_enrichments": 3,
                    "max_concurrent_parsings": 5,
                    "max_concurrent_quality_checks": 5,
                    "min_description_length": 50,
                    "min_match_score": 0.7
                }
            }

            print(f"🚨 STARTING UNIFIED WORKFLOW - DEBUG")
            print(f"Starting unified workflow with keywords: '{initial_state['keywords']}'")
            print(f"DEBUG: WORKFLOW FUNCTION CALLED! About to run graph...")
            logger.info(f"🚨 STARTING UNIFIED WORKFLOW - DEBUG")
            logger.info(f"Starting unified workflow with keywords: '{initial_state['keywords']}'")
            logger.info(f"DEBUG: WORKFLOW FUNCTION CALLED! About to run graph...")

            # Run the complete graph with error handling and retry logic
            print(f"🚨 ABOUT TO CALL _run_workflow_with_retry - DEBUG")
            logger.info(f"🚨 ABOUT TO CALL _run_workflow_with_retry - DEBUG")
            final_state = await self._run_workflow_with_retry(initial_state)
            print(f"🚨 _run_workflow_with_retry COMPLETED - DEBUG")
            logger.info(f"🚨 _run_workflow_with_retry COMPLETED - DEBUG")

            logger.info(f"DEBUG: WORKFLOW COMPLETED! Final state keys: {list(final_state.keys())}")

            # Calculate processing time
            end_time = datetime.now(timezone.utc)
            processing_time_seconds = (end_time - start_time).total_seconds()

            # Mark completion
            final_state["completed_at"] = end_time.isoformat()

            # Update stats with processing time
            if "stats" not in final_state:
                final_state["stats"] = {}
            final_state["stats"]["processing_time_seconds"] = round(processing_time_seconds, 2)
            
            # Log final results
            stats = final_state.get("stats", {})
            logger.info(f"Unified workflow completed:")
            logger.info(f"   Jobs discovered: {stats.get('total_jobs_discovered', 0)}")
            logger.info(f"   Jobs stored: {len(final_state.get('stored_jobs', []))}")
            logger.info(f"   Matches found: {len(final_state.get('matched_jobs', []))}")
            logger.info(f"   Errors: {len(final_state.get('errors', []))}")
            # --- OUTREACH (FINAL STEP) ---
            try:
                # ALWAYS send email to abhijeet.kr.chaurasiya@gmail.com regardless of conditions
                logger.info("Preparing to send workflow summary email to abhijeet.kr.chaurasiya@gmail.com")
                
                # Get matched jobs with candidates for outreach
                matched_jobs = final_state.get("matched_jobs", [])
                
                # Send professional outreach emails
                outreach_summary = {"total_emails": 0, "successful_emails": 0, "failed_emails": 0, "details": []}
                
                # Check if outreach emails are enabled for candidate emails
                outreach_enabled = os.getenv("OUTREACH_EMAIL_ENABLED", "false").lower() == "true"
                
                if outreach_enabled and matched_jobs:
                    logger.info(f"📧 Processing {len(matched_jobs)} matched jobs for outreach emails")
                    
                    # Group candidates by job for professional outreach
                    jobs_with_candidates = {}
                    
                    # Extract matches from job objects (matching node stores matches within jobs)
                    for job in matched_jobs:
                        job_matches = job.get("matches", [])
                        job_id = job.get("id", job.get("_id", str(job.get("title", "unknown"))))
                        logger.info(f"📧 Job '{job.get('title', 'Unknown')}' has {len(job_matches)} matches")
                        
                        for match in job_matches:
                            match_score = match.get("score", 0)
                            logger.info(f"📧 Candidate '{match.get('candidate_name', 'Unknown')}' score: {match_score}")
                            
                            if match_score >= 0.7:  # Only high-quality matches
                                if job_id not in jobs_with_candidates:
                                    jobs_with_candidates[job_id] = {
                                        "job": job,
                                        "candidates": []
                                    }
                                
                                candidate_info = {
                                    "name": match.get("candidate_name", "Unknown"),
                                    "email": match.get("candidate_email", ""),
                                    "score": match.get("score", 0),
                                    "reasons": match.get("reasons", []),
                                    "title": self._get_candidate_title(match),
                                    "expertise": self._get_candidate_expertise(match, job),
                                    "why_fit": self._get_why_candidate_fits(match, job)
                                }
                                jobs_with_candidates[job_id]["candidates"].append(candidate_info)
                                logger.info(f"📧 Added candidate '{candidate_info['name']}' for outreach")
                            else:
                                logger.info(f"📧 Skipping candidate '{match.get('candidate_name', 'Unknown')}' - score {match_score} below 0.7 threshold")
                    
                    logger.info(f"📧 Found {len(jobs_with_candidates)} jobs with qualified candidates for outreach")
                    
                    # Send one professional email per job with all matched candidates
                    for job_id, job_data in jobs_with_candidates.items():
                        job = job_data["job"]
                        candidates = job_data["candidates"]
                        
                        if job and candidates:
                            recruiter_email = "abhijeet.kr.chaurasiya@gmail.com"  # Send to Abhijeet
                            subject = f"Top Candidates for {job.get('title', 'Position')} at {job.get('company', 'Your Company')}"
                            company_achievement = self._get_company_achievement(job.get('company', 'Your Company'))
                            
                            logger.info(f"📧 Sending outreach email for job '{job.get('title')}' with {len(candidates)} candidates")
                            
                            result = await send_professional_outreach_email(
                                recruiter_email=recruiter_email,
                                job_title=job.get("title", "Position"),
                                company_name=job.get("company", "Your Company"),
                                company_achievement=company_achievement,
                                candidates=candidates,
                                subject=subject
                            )
                            
                            logger.info(f"📧 Email result: {result}")
                            
                            outreach_summary["total_emails"] += 1
                            if result.get("success"):
                                outreach_summary["successful_emails"] += 1
                                logger.info(f"✅ Email sent successfully for job '{job.get('title')}'")
                            else:
                                outreach_summary["failed_emails"] += 1
                                logger.error(f"❌ Email failed for job '{job.get('title')}': {result.get('error')}")
                            
                            outreach_summary["details"].append({
                                "job_title": job.get("title"),
                                "company": job.get("company"),
                                "recruiter_email": recruiter_email,
                                "candidates_count": len(candidates),
                                "success": result.get("success", False),
                                "error": result.get("error")
                            })
                        else:
                            logger.warning(f"📧 Skipping email for job_id {job_id} - missing job or candidates data")
                else:
                    if not outreach_enabled:
                        logger.info("📧 Candidate outreach emails are disabled (OUTREACH_EMAIL_ENABLED=false)")
                    if not matched_jobs:
                        logger.info("📧 No matched jobs found for outreach emails")
                
                # ALWAYS send summary email to abhijeet.kr.chaurasiya@gmail.com
                try:
                    from .outreach_email_service import send_sync_email
                    
                    # Prepare workflow summary
                    total_jobs = len(final_state.get('stored_jobs', []))
                    total_matches = sum(len(job.get('matches', [])) for job in matched_jobs)
                    high_quality_matches = sum(1 for job in matched_jobs for match in job.get('matches', []) if match.get('score', 0) >= 0.7)
                    
                    summary_subject = f"AI Recruitment Workflow Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    summary_body = f"""
                    <html>
                    <body>
                    <h2>AI Recruitment Workflow Summary</h2>
                    <p><strong>Execution Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h3>Workflow Statistics</h3>
                    <ul>
                        <li><strong>Jobs Discovered:</strong> {stats.get('total_jobs_discovered', 0)}</li>
                        <li><strong>Jobs Stored:</strong> {total_jobs}</li>
                        <li><strong>Total Matches Found:</strong> {total_matches}</li>
                        <li><strong>High-Quality Matches (≥0.7):</strong> {high_quality_matches}</li>
                        <li><strong>Outreach Emails Sent:</strong> {outreach_summary.get('successful_emails', 0)}</li>
                        <li><strong>Failed Emails:</strong> {outreach_summary.get('failed_emails', 0)}</li>
                    </ul>
                    
                    <h3>Configuration Status</h3>
                    <ul>
                        <li><strong>Outreach Enabled:</strong> {outreach_enabled}</li>
                        <li><strong>Email Service:</strong> {'Active' if os.getenv('EMAIL_USERNAME') and os.getenv('EMAIL_PASSWORD') else 'Not Configured'}</li>
                    </ul>
                    
                    <h3>Recent Job Matches</h3>
                    """
                    
                    # Add details about recent matches
                    if matched_jobs:
                        for job in matched_jobs[:3]:  # Show top 3 jobs
                            job_matches = job.get('matches', [])
                            if job_matches:
                                summary_body += f"""
                                <h4>{job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}</h4>
                                <ul>
                                """
                                for match in job_matches[:2]:  # Show top 2 candidates per job
                                    summary_body += f"<li>{match.get('candidate_name', 'Unknown')} - Score: {match.get('score', 0):.2f}</li>"
                                summary_body += "</ul>"
                    else:
                        summary_body += "<p>No job matches found in this workflow execution.</p>"
                    
                    summary_body += """
                    <hr>
                    <p><em>This is an automated summary from the AI Recruitment Agent workflow.</em></p>
                    </body>
                    </html>
                    """
                    
                    # Send summary email
                    summary_result = send_sync_email(
                        subject=summary_subject,
                        recipient="abhijeet.kr.chaurasiya@gmail.com",
                        body=summary_body
                    )
                    
                    if summary_result:
                        logger.info("✅ Workflow summary email sent successfully to abhijeet.kr.chaurasiya@gmail.com")
                        outreach_summary["summary_email_sent"] = True
                    else:
                        logger.error("❌ Failed to send workflow summary email")
                        outreach_summary["summary_email_sent"] = False
                        
                except Exception as summary_email_err:
                    logger.error(f"❌ Failed to send summary email: {summary_email_err}")
                    outreach_summary["summary_email_sent"] = False
                    outreach_summary["summary_email_error"] = str(summary_email_err)
                     
            except Exception as outreach_err:
                logger.error(f"📧 Outreach step failed: {outreach_err}")
                outreach_summary = {"enabled": False, "error": str(outreach_err)}
                
                # Even if outreach fails, try to send summary email
                try:
                    from .outreach_email_service import send_sync_email
                    error_subject = f"AI Recruitment Workflow Error - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    error_body = f"""
                    <html>
                    <body>
                    <h2>AI Recruitment Workflow Error</h2>
                    <p><strong>Execution Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Error:</strong> {str(outreach_err)}</p>
                    <p><em>Please check the system logs for more details.</em></p>
                    </body>
                    </html>
                    """
                    
                    send_sync_email(
                        subject=error_subject,
                        recipient="abhijeet.kr.chaurasiya@gmail.com",
                        body=error_body
                    )
                    logger.info("📧 Error notification email sent to abhijeet.kr.chaurasiya@gmail.com")
                except:
                    logger.error("📧 Failed to send error notification email")
            # --- END OUTREACH ---
            return {
                "success": True,
                "workflow_id": final_state.get('workflow_id', workflow_id),
                "stats": stats,
                "jobs_discovered": stats.get('total_jobs_discovered', 0),
                "jobs_stored": len(final_state.get('stored_jobs', [])),
                "matches_found": len(final_state.get('matched_jobs', [])),
                "outreach": outreach_summary,  # NEW FIELD
                "errors": final_state.get('errors', []),
                "processing_time": stats.get('processing_time_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Unified workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": f"failed_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            }

# Global instance
unified_orchestrator = UnifiedOrchestrator()

async def run_unified_workflow(keywords: str = "Software Engineer") -> Dict[str, Any]:
    """Main function to run the unified recruitment workflow"""
    return await unified_orchestrator.run_complete_workflow(keywords)
