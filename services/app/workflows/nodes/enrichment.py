"""
Enhanced Enrichment Node using Apollo API with Companies/Contacts Collections
"""

import logging
from typing import Dict, Any
from ...services.enrichment_service import enrichment_service

logger = logging.getLogger(__name__)

async def enrichment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich jobs with company and contact data using enhanced Apollo API integration"""
    logger.info("🔄 Starting enhanced enrichment with companies/contacts collections")

    deduplicated_jobs = state.get("deduplicated_jobs", [])
    if not deduplicated_jobs:
        state["enriched_jobs"] = []
        return state

    enriched_jobs = []
    enrichment_stats = {
        "total_jobs": len(deduplicated_jobs),
        "companies_created": 0,
        "contacts_created": 0,
        "apollo_enriched": 0,
        "manual_fallback": 0
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

                    if enrichment_result["enrichment_source"] == "apollo":
                        enrichment_stats["apollo_enriched"] += 1
                    else:
                        enrichment_stats["manual_fallback"] += 1

                    enriched_jobs.append(job)
                    logger.info(f"✅ Enriched {company_name}: Company ID {enrichment_result['company_id']}, {enrichment_result['contacts_count']} contacts")
                else:
                    # Failed enrichment - skip job
                    logger.error(f"❌ Failed to enrich {company_name}: {enrichment_result.get('error', 'Unknown error')}")
                    continue

            except Exception as e:
                logger.error(f"❌ Enrichment error for {company_name}: {e}")
                continue
        else:
            logger.warning(f"⚠️ No company name found, skipping job")
            continue

    # Store enrichment statistics
    state["enriched_jobs"] = enriched_jobs
    state["enrichment_stats"] = enrichment_stats

    logger.info(f"✅ Enhanced enrichment complete:")
    logger.info(f"   📊 Jobs processed: {enrichment_stats['total_jobs']}")
    logger.info(f"   🏢 Companies created/found: {enrichment_stats['companies_created']}")
    logger.info(f"   👥 Contacts created/found: {enrichment_stats['contacts_created']}")
    logger.info(f"   🚀 Apollo enriched: {enrichment_stats['apollo_enriched']}")
    logger.info(f"   📝 Manual fallback: {enrichment_stats['manual_fallback']}")
    logger.info(f"   ✅ Jobs enriched: {len(enriched_jobs)}")

    return state
