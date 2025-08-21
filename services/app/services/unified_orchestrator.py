"""
Unified LangGraph Orchestrator
Complete recruitment pipeline: Scraping → Processing → Matching → Storage
Replaces both agent_orchestrator.py and base_workflow.py
"""
import logging
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
        workflow.add_edge("match", "store")            # Store everything
        workflow.add_edge("store", END)
        
        return workflow.compile()

    # Initialization Node
    async def _init_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Initialize the workflow state"""
        logger.info("🚀 Starting unified recruitment workflow")
        logger.info(f"🔍 Keywords: {state['keywords']}")
        return state

    # Scraping Nodes (Parallel)
    async def _linkedin_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """LinkedIn scraping agent"""
        try:
            logger.info("🔍 Running LinkedIn agent...")
            jobs = await fetch_linkedin_jobs(state["keywords"])
            state["linkedin_jobs"] = jobs
            logger.info(f"✅ LinkedIn: {len(jobs)} jobs found")
        except Exception as e:
            logger.error(f"❌ LinkedIn agent failed: {e}")
            state["linkedin_jobs"] = []
            state["errors"].append(f"LinkedIn: {str(e)}")
        return state
    
    async def _indeed_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Indeed scraping agent"""
        try:
            logger.info("🔍 Running Indeed agent...")
            jobs = await fetch_indeed_jobs(state["keywords"])
            state["indeed_jobs"] = jobs
            logger.info(f"✅ Indeed: {len(jobs)} jobs found")
        except Exception as e:
            logger.error(f"❌ Indeed agent failed: {e}")
            state["indeed_jobs"] = []
            state["errors"].append(f"Indeed: {str(e)}")
        return state
    
    async def _google_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Google Jobs scraping agent"""
        try:
            logger.info("🔍 Running Google agent...")
            jobs = await fetch_google_jobs(state["keywords"])
            state["google_jobs"] = jobs
            logger.info(f"✅ Google: {len(jobs)} jobs found")
        except Exception as e:
            logger.error(f"❌ Google agent failed: {e}")
            state["google_jobs"] = []
            state["errors"].append(f"Google: {str(e)}")
        return state
    
    # Aggregation Node
    async def _aggregate_node(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Aggregate all scraping results"""
        try:
            logger.info("📊 Aggregating scraping results...")
            
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
            
            logger.info(f"📊 Aggregated {len(all_jobs)} total jobs")
            
        except Exception as e:
            logger.error(f"❌ Aggregation failed: {e}")
            state["raw_jobs"] = []
            state["errors"].append(f"Aggregation: {str(e)}")
        
        return state
    
    # Processing Node Wrappers (Sequential)
    async def _deduplication_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for deduplication node"""
        logger.info("🔄 Step 2: Deduplication")
        result = await deduplication_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state

    async def _enrichment_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for enrichment node"""
        logger.info("🔄 Step 3: Enrichment")
        result = await enrichment_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state

    async def _parsing_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for parsing node"""
        logger.info("🔄 Step 4: Parsing")
        result = await parsing_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state

    async def _quality_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for quality check node"""
        logger.info("🔄 Step 5: Quality Check")
        result = await quality_check_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state
    
    async def _matching_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for matching node"""
        logger.info("🔄 Step 6: Matching")
        result = await matching_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state

    async def _storage_wrapper(self, state: UnifiedRecruitmentState) -> UnifiedRecruitmentState:
        """Wrapper for storage node"""
        logger.info("🔄 Step 7: Storage")
        result = await storage_node(dict(state))
        for key, value in result.items():
            if key in state:
                state[key] = value
        return state
    
    # Main execution method
    async def run_complete_workflow(self, keywords: str = "Software Engineer") -> Dict[str, Any]:
        """Run the complete recruitment workflow"""
        try:
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

            logger.info(f"🚀 Starting unified workflow with keywords: '{initial_state['keywords']}'")

            # Run the complete graph
            final_state = await self.graph.ainvoke(initial_state)

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
            logger.info(f"🎯 Unified workflow completed:")
            logger.info(f"   Jobs discovered: {stats.get('total_jobs_discovered', 0)}")
            logger.info(f"   Jobs stored: {len(final_state.get('stored_jobs', []))}")
            logger.info(f"   Matches found: {len(final_state.get('matched_jobs', []))}")
            logger.info(f"   Errors: {len(final_state.get('errors', []))}")
            
            return {
                "success": True,
                "workflow_id": final_state.get('workflow_id', workflow_id),
                "stats": stats,
                "jobs_discovered": stats.get('total_jobs_discovered', 0),
                "jobs_stored": len(final_state.get('stored_jobs', [])),
                "matches_found": len(final_state.get('matched_jobs', [])),
                "errors": final_state.get('errors', []),
                "processing_time": stats.get('processing_time_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Unified workflow failed: {e}")
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
