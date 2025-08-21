import os
import asyncio
import logging
from email.message import EmailMessage  # kept for structure reuse
from dotenv import load_dotenv
import httpx
from typing import List, Dict, Any

from ..config.database import connect_to_mongo, close_mongo_connection
from ..services.contact_service import contact_service

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ENABLED = os.getenv("OUTREACH_EMAIL_ENABLED", "false").lower() == "true"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")  # NEW
FROM_EMAIL = os.getenv("OUTREACH_FROM", "Recruitment Agent <no-reply@yourdomain.com>")
MAX_CONTACTS = int(os.getenv("OUTREACH_MAX_CONTACTS", "5"))
RESEND_API_BASE = "https://api.resend.com"

def _build_message(contact_email: str, contact_name: str) -> dict:
    """Return JSON payload for Resend API."""
    subject = "Test Outreach Email"
    body = f"""Hi {contact_name or 'there'},

This is a test outreach email from the AI Recruitment Agent.
If you received this, the Resend integration is working ✅.

Regards,
Outreach Bot
"""
    return {
        "from": FROM_EMAIL,
        "to": [contact_email],
        "subject": subject,
        "text": body
    }

async def _send_email(payload: dict) -> bool:
    """Send email via Resend API."""
    if not RESEND_API_KEY:
        logger.error("RESEND_API_KEY not set")
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{RESEND_API_BASE}/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
        if resp.status_code in (200, 202):
            return True
        logger.error(f"Resend error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.error(f"Resend request failed: {e}")
        return False

async def send_test_emails():
    summary = {
        "enabled": ENABLED,
        "contacts_targeted": 0,
        "emails_attempted": 0,
        "emails_sent": 0,
        "errors": []
    }

    if not ENABLED:
        print("[Outreach] Disabled (OUTREACH_EMAIL_ENABLED=false)")
        return summary
    if not RESEND_API_KEY:
        print("[Outreach] Missing RESEND_API_KEY")
        summary["errors"].append("missing_resend_api_key")
        return summary

    contacts = await contact_service.get_all_contacts(limit=MAX_CONTACTS)
    if not contacts:
        print("[Outreach] No contacts in DB")
        return summary

    for c in contacts:
        email = getattr(c, "email", None)
        name = getattr(c, "name", None)
        if not email:
            continue
        summary["contacts_targeted"] += 1
        payload = _build_message(email, name)
        summary["emails_attempted"] += 1
        print(f"[Outreach] Sending to {email} via Resend ...")
        if await _send_email(payload):
            summary["emails_sent"] += 1
            print(f"[Outreach] ✅ Sent {email}")
        else:
            print(f"[Outreach] ❌ Failed {email}")

    print(f"[Outreach] Summary: {summary}")
    return summary

async def send_outreach_emails(stored_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Final workflow outreach hook.
    Currently ignores stored_jobs (no per-job targeting yet) and just
    sends simple emails to the first N contacts.
    """
    summary: Dict[str, Any] = {
        "enabled": ENABLED,
        "contacts_targeted": 0,
        "emails_attempted": 0,
        "emails_sent": 0,
        "errors": [],
        "jobs_context": len(stored_jobs or []),
    }
    if not ENABLED:
        return summary
    if not RESEND_API_KEY:
        summary["errors"].append("missing_resend_api_key")
        return summary
    try:
        contacts = await contact_service.get_all_contacts(limit=MAX_CONTACTS)
    except Exception as e:
        logger.error(f"Failed to load contacts: {e}")
        summary["errors"].append("contacts_load_failed")
        return summary
    if not contacts:
        return summary
    for c in contacts:
        email = getattr(c, "email", None)
        name = getattr(c, "name", None)
        if not email:
            continue
        summary["contacts_targeted"] += 1
        payload = _build_message(email, name)
        summary["emails_attempted"] += 1
        if await _send_email(payload):
            summary["emails_sent"] += 1
        else:
            summary["errors"].append(f"send_fail:{email}")
    return summary

async def main():
    await connect_to_mongo()
    try:
        await send_test_emails()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())