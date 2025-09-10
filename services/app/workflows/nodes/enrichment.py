"""
Enhanced Enrichment Node using Apollo API with Companies/Contacts Collections
"""

import logging
import traceback
from typing import Dict, Any
from ...services.enrichment_service import enrichment_service
logger = logging.getLogger(__name__)

async def enrichment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich jobs with company and contact data using enhanced Apollo API integration"""
    logger.info("DEBUG: ENRICHMENT NODE CALLED!")
    logger.info("Starting enhanced enrichment with companies/contacts collections")
    logger.info(f"State keys in enrichment: {list(state.keys())}")

    deduplicated_jobs = state.get("deduplicated_jobs", [])
    logger.info(f"🔄 Deduplicated jobs count: {len(deduplicated_jobs)}")

    # Debug: Check what enrichment receives
    if deduplicated_jobs:
        sample_job = deduplicated_jobs[0]
        logger.info(f"ENRICHMENT INPUT DEBUG: Sample job received:")
        logger.info(f"   Title: {sample_job.get('title', 'Unknown')}")
        logger.info(f"   Processing Status: {sample_job.get('processing_status', 'Unknown')}")
        logger.info(f"   Job Type: {sample_job.get('job_type', 'None')}")
        logger.info(f"   Requirements: {len(sample_job.get('requirements', []))} items")

    if not deduplicated_jobs:
        state["enriched_jobs"] = []
        return state

    enriched_jobs = []
    enrichment_stats = {
        "total_jobs": len(deduplicated_jobs),
        "companies_created": 0,
        "contacts_created": 0,
        "apollo_enriched": 0,
    }

    for job in deduplicated_jobs:
        company_name = job.get("company")
        if company_name:
            try:
                # Use enrichment service
                enrichment_result = await enrichment_service.enrich_company_and_contacts(company_name)

                if enrichment_result["company_id"]:
                    # Success - link job to company
                    job["company_id"] = enrichment_result["company_id"]
                    job["company_data"] = enrichment_result["company_data"]

                    # Update stats
                    enrichment_stats["companies_created"] += 1
                    enrichment_stats["contacts_created"] += enrichment_result["contacts_count"]

                    # Check if company was enriched via Apollo
                    company_data = enrichment_result.get("company_data")
                    if company_data and hasattr(company_data, 'enrichment_source') and company_data.enrichment_source == "apollo":
                        enrichment_stats["apollo_enriched"] += 1

                    # Create enriched job preserving all parsed fields
                    enriched_job = job.copy()  # Preserve all parsed fields
                    enriched_job["company_id"] = enrichment_result["company_id"]
                    enriched_job["enrichment_status"] = "enriched"

                    enriched_jobs.append(enriched_job)
                    logger.info(
                        f"✅ Enriched {company_name}: Company ID {enrichment_result['company_id']}, {enrichment_result['contacts_count']} contacts"
                    )

                    # Enrichment completed successfully
                else:
                    # Failed enrichment - still preserve parsed fields
                    logger.error(
                        f"❌ Failed to enrich {company_name}: {enrichment_result.get('error', 'Unknown error')}"
                    )
                    # Add job without enrichment but preserve parsed fields
                    enriched_job = job.copy()
                    enriched_job["enrichment_status"] = "failed"
                    enriched_jobs.append(enriched_job)

            except Exception as e:
                logger.error(f"❌ Enrichment error for {company_name}: {e}")
                traceback.print_exc()
                # Still preserve parsed fields even on exception
                enriched_job = job.copy()
                enriched_job["enrichment_status"] = "error"
                enriched_jobs.append(enriched_job)
        else:
            logger.warning(f"⚠️ No company name found, skipping job")
            # Still preserve parsed fields even without company name
            enriched_job = job.copy()
            enriched_job["enrichment_status"] = "no_company"
            enriched_jobs.append(enriched_job)
            continue

    # Store enrichment statistics
    state["enriched_jobs"] = enriched_jobs
    state["enrichment_stats"] = enrichment_stats

    logger.info(f"✅ Enhanced enrichment complete:")
    logger.info(f"   📊 Jobs processed: {enrichment_stats['total_jobs']}")
    logger.info(f"   🏢 Companies created/found: {enrichment_stats['companies_created']}")
    logger.info(f"   👥 Contacts created: {enrichment_stats['contacts_created']}")
    logger.info(f"   🚀 Apollo enriched: {enrichment_stats['apollo_enriched']}")
    logger.info(f"   ✅ Jobs enriched: {len(enriched_jobs)}")

    return state
