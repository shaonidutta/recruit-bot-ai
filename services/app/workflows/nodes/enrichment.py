"""
Enhanced Enrichment Node using Apollo API with Companies/Contacts Collections
Optimized with parallel processing and caching for production performance
"""

import logging
import traceback
import asyncio
from typing import Dict, Any
from ...services.enrichment_service import enrichment_service
from ...utils.parallel_processing import parallel_processor, performance_monitor
from ...utils.caching import cache_manager, cached_company_enrichment
logger = logging.getLogger(__name__)

@cached_company_enrichment(ttl=86400)  # Cache for 24 hours
async def get_cached_company_enrichment(company_name: str) -> Dict[str, Any]:
    """Get company enrichment with caching"""
    return await enrichment_service.enrich_company_and_contacts(company_name)

async def enrich_single_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich a single job with company data - optimized with caching and parallel processing"""
    company_name = job.get("company")
    if not company_name:
        return job

    try:
        # Use cached enrichment service for production performance
        enrichment_result = await get_cached_company_enrichment(company_name)

        if enrichment_result["company_id"]:
            # Success - link job to company
            job["company_id"] = enrichment_result["company_id"]
            job["company_data"] = enrichment_result["company_data"]
            job["enrichment_success"] = True
            job["contacts_count"] = enrichment_result["contacts_count"]

            # Check if company was enriched via Apollo
            company_data = enrichment_result.get("company_data")
            if company_data and hasattr(company_data, 'enrichment_source') and company_data.enrichment_source == "apollo":
                job["apollo_enriched"] = True
        else:
            job["enrichment_success"] = False

    except asyncio.TimeoutError:
        logger.warning(f"Enrichment timeout for company: {company_name}")
        job["enrichment_success"] = False
        job["enrichment_error"] = "timeout"
    except Exception as e:
        logger.error(f"Enrichment failed for {company_name}: {e}")
        job["enrichment_success"] = False
        job["enrichment_error"] = str(e)

    return job

@performance_monitor("Enhanced Enrichment (Parallel)")
async def enrichment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich jobs with company and contact data using parallel processing"""
    logger.info("Starting enhanced enrichment with parallel processing")

    deduplicated_jobs = state.get("deduplicated_jobs", [])

    print(f"🔍 DEBUG ENRICHMENT: Available state keys: {list(state.keys())}")
    print(f"🔍 DEBUG ENRICHMENT: Deduplicated jobs: {len(deduplicated_jobs)}")

    if deduplicated_jobs:
        first_job = deduplicated_jobs[0]
        print(f"🔍 DEBUG ENRICHMENT: First job to enrich: {first_job.get('title')} at {first_job.get('company')}")

    if not deduplicated_jobs:
        state["enriched_jobs"] = []
        return state

    # Process jobs in parallel batches with aggressive caching optimization
    enriched_jobs = await parallel_processor.process_jobs_in_batches(
        jobs=deduplicated_jobs,
        processor_func=enrich_single_job,
        batch_size=10,  # Larger batches since cache reduces API calls
        max_concurrent_batches=5  # More aggressive since cache handles duplicates
    )

    # Calculate enrichment statistics
    enrichment_stats = {
        "total_jobs": len(deduplicated_jobs),
        "companies_created": sum(1 for job in enriched_jobs if job.get("enrichment_success")),
        "contacts_created": sum(job.get("contacts_count", 0) for job in enriched_jobs),
        "apollo_enriched": sum(1 for job in enriched_jobs if job.get("apollo_enriched")),
        "timeouts": sum(1 for job in enriched_jobs if job.get("enrichment_error") == "timeout"),
        "errors": sum(1 for job in enriched_jobs if job.get("enrichment_error") and job.get("enrichment_error") != "timeout")
    }

    # Store enrichment statistics
    state["enriched_jobs"] = enriched_jobs
    state["enrichment_stats"] = enrichment_stats

    if enriched_jobs:
        first_job = enriched_jobs[0]
        print(f"🔍 DEBUG ENRICHMENT OUTPUT: First enriched job: {first_job.get('title')} at {first_job.get('company')}")

    logger.info(f"✅ Parallel enrichment complete:")
    logger.info(f"   📊 Jobs processed: {enrichment_stats['total_jobs']}")
    logger.info(f"   🏢 Companies created/found: {enrichment_stats['companies_created']}")
    logger.info(f"   👥 Contacts created: {enrichment_stats['contacts_created']}")
    logger.info(f"   🚀 Apollo enriched: {enrichment_stats['apollo_enriched']}")
    logger.info(f"   ⏱️ Timeouts: {enrichment_stats['timeouts']}")
    logger.info(f"   ❌ Errors: {enrichment_stats['errors']}")
    logger.info(f"   ✅ Jobs enriched: {len(enriched_jobs)}")

    return state
