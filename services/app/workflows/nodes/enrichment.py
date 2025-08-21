"""
Enhanced Enrichment Node using Apollo API with Companies/Contacts Collections
"""

import logging
import traceback
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from ...services.enrichment_service import enrichment_service
from ...config.database import get_database

logger = logging.getLogger(__name__)

# normalize phone → keep only digits
_norm = lambda s: re.sub(r"\D", "", (s or ""))


async def fallback_enrich_company(company_name: str, db, contacts_path: str = None) -> Dict[str, Any]:
    """
    Simple fallback: import all contacts from contacts.json.
    Logic:
      For every entry with an email:
        - If email already exists in contacts collection -> skip
        - Else insert
    Ignores the company_name passed in (kept only for call signature compatibility).
    """
    print(f"\n--- Fallback (bulk import) triggered (company param='{company_name}') ---")

    if db is None:
        print("❌ ERROR: DB handle is None. Did you call connect_to_mongo() at startup?")
        return {"contacts_count": 0, "error": "no_db"}

    # Resolve contacts.json (services/contacts.json)
    here = Path(__file__).resolve()
    path = Path(contacts_path) if contacts_path else (here.parents[3] / "contacts.json")
    print(f"📁 Looking for contacts.json at: {path}")

    if not path.exists():
        print("❌ ERROR: contacts.json not found.")
        return {"contacts_count": 0, "error": "contacts_json_not_found"}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ ERROR: Failed to read/parse contacts.json: {e}")
        return {"contacts_count": 0, "error": f"parse_error:{e}"}

    # Accept either a list or {"contacts":[...]}
    if isinstance(data, dict) and "contacts" in data:
        contacts = data["contacts"]
    else:
        contacts = data

    if not isinstance(contacts, list):
        print("❌ ERROR: contacts.json content is not a list.")
        return {"contacts_count": 0, "error": "invalid_format"}

    total = len(contacts)
    print(f"📊 Loaded {total} raw entries from contacts.json")

    coll = db.contacts
    inserted = 0
    skipped_existing = 0
    skipped_no_email = 0
    inserted_ids = []

    for idx, c in enumerate(contacts, start=1):
        email = (c.get("email") or "").strip().lower()
        if not email:
            skipped_no_email += 1
            if skipped_no_email <= 5:  # avoid flooding
                print(f"  [{idx}/{total}] SKIP (no email) name='{c.get('name')}'")
            continue

        existing = await coll.find_one({"email": email}, {"_id": 1})
        if existing:
            skipped_existing += 1
            if skipped_existing <= 5:
                print(f"  [{idx}/{total}] SKIP (exists) email='{email}'")
            continue

        doc = {
            "name": c.get("name"),
            "email": email,
            "phone": (c.get("mob_no") or "").strip() or None,
            "company_name": c.get("company_name"),
            "enrichment_source": "fallback",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        # Remove None fields
        doc = {k: v for k, v in doc.items() if v is not None}

        try:
            res = await coll.insert_one(doc)
            inserted += 1
            inserted_ids.append(str(res.inserted_id))
            if inserted <= 5:
                print(f"  [{idx}/{total}] INSERT email='{email}' id={res.inserted_id}")
        except Exception as e:
            print(f"  [{idx}/{total}] ERROR inserting email='{email}': {e}")

    print("✅ Import summary:")
    print(f"   • Total entries processed: {total}")
    print(f"   • Inserted new: {inserted}")
    print(f"   • Skipped existing email: {skipped_existing}")
    print(f"   • Skipped no email: {skipped_no_email}")

    result = {
        "contacts_count": inserted,          # kept for existing enrichment stats
        "inserted_count": inserted,
        "inserted_ids": inserted_ids,
        "skipped_existing": skipped_existing,
        "skipped_no_email": skipped_no_email,
        "total_in_file": total,
        "file_used": str(path),
        "mode": "bulk_all"
    }
    print(f"--- End Fallback (bulk import) ---\n")
    return result


async def enrichment_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich jobs with company and contact data using enhanced Apollo API integration"""
    logger.info("🔄 Starting enhanced enrichment with companies/contacts collections")

    # Get the database object
    db = get_database()

    deduplicated_jobs = state.get("deduplicated_jobs", [])
    if not deduplicated_jobs:
        state["enriched_jobs"] = []
        return state

    enriched_jobs = []
    enrichment_stats = {
        "total_jobs": len(deduplicated_jobs),
        "companies_created": 0,
        "contacts_created": 0,
        "contacts_updated": 0,
        "apollo_enriched": 0,
        "manual_fallback": 0,
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
                    logger.info(
                        f"✅ Enriched {company_name}: Company ID {enrichment_result['company_id']}, {enrichment_result['contacts_count']} contacts"
                    )

                    # If enrichment succeeded but not performed by Apollo, run fallback too
                    if enrichment_result.get("enrichment_source") != "apollo":
                        try:
                            fallback_result = await fallback_enrich_company(company_name, db)
                            enrichment_stats["contacts_created"] += fallback_result.get("contacts_count", 0)
                            enrichment_stats["contacts_updated"] += fallback_result.get("updated_count", 0)
                            print(f"🔁 Fallback (post-enrich) result for {company_name}: {fallback_result}")
                        except Exception:
                            print("Fallback enrichment also failed during post-enrich step")
                            traceback.print_exc()
                else:
                    # Failed enrichment - invoke fallback
                    logger.error(
                        f"❌ Failed to enrich {company_name}: {enrichment_result.get('error', 'Unknown error')}"
                    )
                    fallback_result = await fallback_enrich_company(company_name, db)
                    enrichment_stats["contacts_created"] += fallback_result.get("contacts_count", 0)
                    enrichment_stats["contacts_updated"] += fallback_result.get("updated_count", 0)
                    print(f"🔁 Fallback result for {company_name}: {fallback_result}")
                    continue

            except Exception as e:
                logger.error(f"❌ Enrichment error for {company_name}: {e}")
                # call fallback helper on unexpected exception
                try:
                    fallback_result = await fallback_enrich_company(company_name, db)
                    enrichment_stats["contacts_created"] += fallback_result.get("contacts_count", 0)
                    enrichment_stats["contacts_updated"] += fallback_result.get("updated_count", 0)
                    print(f"🔁 Fallback result after exception for {company_name}: {fallback_result}")
                except Exception:
                    print("Fallback enrichment also failed")
                    traceback.print_exc()
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
    logger.info(f"   👥 Contacts created: {enrichment_stats['contacts_created']}")
    logger.info(f"   ✏️ Contacts updated: {enrichment_stats['contacts_updated']}")
    logger.info(f"   🚀 Apollo enriched: {enrichment_stats['apollo_enriched']}")
    logger.info(f"   📝 Manual fallback: {enrichment_stats['manual_fallback']}")
    logger.info(f"   ✅ Jobs enriched: {len(enriched_jobs)}")

    return state
