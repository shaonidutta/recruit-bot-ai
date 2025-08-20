# services/app/services.py
"""
Orchestration layer for AI Recruitment Agent workflows
Combines discovery, enrichment, parsing, and matching services
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

# Database operations handled by backend - removed database import
from .enrichment_service import get_enrichment_service
from .parsing_service import parse_job_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def store_discovered_job(job_data: Dict[str, Any], platform: str) -> Optional[Dict[str, Any]]:
    """
    Process discovered job data for backend storage
    Why this function? Validates and structures job data before backend storage
    """
    try:
        # Structure job data according to our model
        structured_job = {
            "title": job_data.get("title", ""),
            "company_name": job_data.get("company_name") or job_data.get("company", ""),
            "location": job_data.get("location"),
            "description": job_data.get("description"),
            "source": {
                "platform": platform,
                "agent_run_id": f"run_{int(time.time())}",
                "url": job_data.get("link") or job_data.get("url")
            },
            "status": "discovered",
            "raw_data": job_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"✅ Job processed: {structured_job['title']} at {structured_job['company_name']}")

        # Return structured data for backend to store
        return structured_job

    except Exception as e:
        logger.error(f"❌ Failed to process job: {e}")
        return None


async def process_job_pipeline(job_id: str) -> Dict[str, Any]:
    """
    Complete job processing pipeline: enrichment → parsing → matching
    Why this workflow? Sequential processing ensures data consistency and proper status tracking
    """
    start_time = time.time()

    try:
        logger.info(f"🚀 Starting job pipeline for job: {job_id}")

        # This function now returns processing instructions for backend
        # Backend will handle database operations and orchestration
        return {
            "success": True,
            "message": "Pipeline processing moved to backend",
            "instructions": {
                "steps": [
                    "1. Enrich company data using enrichment service",
                    "2. Parse job description using parsing service",
                    "3. Find candidate matches using matching service"
                ],
                "note": "Database operations handled by backend"
            },
            "processing_time": time.time() - start_time
        }



    except Exception as e:
        logger.error(f"❌ Job pipeline failed for {job_id}: {e}")
        return {
            "success": False,
            "message": f"Pipeline failed: {str(e)}",
            "data": None,
            "processing_time": time.time() - start_time
        }


async def enrich_company_standalone(company_name: str) -> Dict[str, Any]:
    """
    Standalone company enrichment for direct API calls
    Why separate function? Allows direct company enrichment without job context
    """
    try:
        enrichment_service = await get_enrichment_service()

        # Enrich company information
        company_data = await enrichment_service.enrich_company(company_name)

        if not company_data:
            return {
                "success": False,
                "message": f"No company data found for: {company_name}",
                "data": None
            }

        return {
            "success": True,
            "message": f"Company enrichment completed for {company_name}",
            "data": {
                "company_data": company_data
            }
        }

    except Exception as e:
        logger.error(f"❌ Company enrichment failed for {company_name}: {e}")
        return {
            "success": False,
            "message": f"Enrichment failed: {str(e)}",
            "data": None
        }


# Batch processing and job matching moved to backend - database operations handled there


# Simple utility functions for data processing
async def parse_job_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse job description and extract structured data
    """
    try:
        description = job_data.get("description", "")
        title = job_data.get("title", "")

        if description:
            parsed_data = parse_job_description(description, title)
            return {
                "success": True,
                "parsed_data": parsed_data
            }

        return {
            "success": False,
            "message": "No description to parse"
        }

    except Exception as e:
        logger.error(f"❌ Job parsing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

