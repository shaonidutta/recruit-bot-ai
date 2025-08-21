import os
import asyncio
from dotenv import load_dotenv
import resend
from typing import List, Dict, Any

from ..config.database import connect_to_mongo, close_mongo_connection
from ..services.contact_service import contact_service

load_dotenv()

# Config
ENABLED = os.getenv("OUTREACH_EMAIL_ENABLED", "false").lower() == "true"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("OUTREACH_FROM", "onboarding@resend.dev")  # Use Resend's default domain
MAX_CONTACTS = int(os.getenv("OUTREACH_MAX_CONTACTS", "5"))

# Set API key using environment variable (like the template)
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    print("⚠️ RESEND_API_KEY not found in environment variables")

# Debug info
print(f"🔑 RESEND_API_KEY present: {bool(RESEND_API_KEY)}")
print(f"🔑 RESEND_API_KEY length: {len(RESEND_API_KEY) if RESEND_API_KEY else 0}")
print(f"🔑 RESEND_API_KEY starts with: {RESEND_API_KEY[:10] if RESEND_API_KEY else 'None'}...")
print(f"📧 FROM_EMAIL: {FROM_EMAIL}")
print(f"⚙️ ENABLED: {ENABLED}")

# Build email payload
def _build_message(contact_email: str, contact_name: str) -> dict:
    subject = "AI Recruitment Agent – Outreach"
    html = f"""
    <p>Hi {contact_name or 'there'},</p>
    <p>This is a <strong>test outreach email</strong> from the AI Recruitment Agent.<br/>
    If you received this, the Resend integration is working ✅.</p>
    <p>Regards,<br/>Outreach Bot</p>"""
    
    # Use exact format from Resend template
    payload = {
        "from": FROM_EMAIL,  # Use simple string format like template
        "to": contact_email,  # Use string, not list
        "subject": subject,
        "html": html
    }
    print(f"📦 Built payload: {payload}")
    return payload

# Send email
def _send_email(payload: dict) -> bool:
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY not set")
        return False
    
    print(f"🚀 Attempting to send email with payload: {payload}")
    print(f"🔑 Using API key: {RESEND_API_KEY[:10]}...")
    
    try:
        # Use the exact format from your Resend template
        email = resend.Emails.send({
            "from": payload["from"],
            "to": payload["to"], 
            "subject": payload["subject"],
            "html": payload["html"]
        })
        
        print(f"📧 Resend response: {email}")
        print(f"📧 Resend response type: {type(email)}")
        
        # Check if we got a successful response with an ID
        if hasattr(email, 'id') or (isinstance(email, dict) and email.get("id")):
            email_id = email.id if hasattr(email, 'id') else email.get('id')
            print(f"✅ Email sent successfully with ID: {email_id}")
            return True
        else:
            print(f"❌ Email send failed - no ID returned: {email}")
            return False
            
    except resend.exceptions.ResendError as re:
        print(f"❌ ResendError occurred:")
        print(f"   📋 Error message: {re}")
        print(f"   📋 Error args: {re.args}")
        print(f"   📋 Error dir: {dir(re)}")
        if hasattr(re, 'message'):
            print(f"   📋 Error message attr: {re.message}")
        if hasattr(re, 'status_code'):
            print(f"   📋 Error status_code: {re.status_code}")
        if hasattr(re, 'response'):
            print(f"   📋 Error response: {re.response}")
        if hasattr(re, 'details'):
            print(f"   📋 Error details: {re.details}")
        return False
    except Exception as e:
        print(f"❌ General error occurred:")
        print(f"   📋 Error message: {e}")
        print(f"   📋 Error type: {type(e)}")
        print(f"   📋 Error args: {e.args}")
        print(f"   📋 Error dir: {dir(e)}")
        return False

# Outreach workflow
async def send_outreach_emails(stored_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "enabled": ENABLED,
        "contacts_targeted": 0,
        "emails_attempted": 0,
        "emails_sent": 0,
        "errors": [],
        "jobs_context": len(stored_jobs or []),
    }

    print(f"[Outreach] Start | enabled={ENABLED} jobs={summary['jobs_context']} max_contacts={MAX_CONTACTS}")

    if not ENABLED:
        return summary
    if not RESEND_API_KEY:
        summary["errors"].append("missing_resend_api_key")
        return summary

    try:
        contacts = await contact_service.get_all_contacts(limit=MAX_CONTACTS)
        print(f"🔍 Loaded {len(contacts)} contacts from database")
    except Exception as e:
        summary["errors"].append("contacts_load_failed")
        print(f"❌ Error loading contacts: {e}")
        return summary

    if not contacts:
        print("[Outreach] No contacts available")
        return summary

    for idx, c in enumerate(contacts, start=1):
        email = getattr(c, "email", None)
        name = getattr(c, "name", None)
        print(f"🔍 Processing contact {idx}: email={email}, name={name}")
        
        if not email:
            print(f"⚠️ Skipping contact {idx} - no email")
            continue

        summary["contacts_targeted"] += 1
        payload = _build_message(email, name)
        summary["emails_attempted"] += 1
        print(f"[Outreach] [{idx}] Sending to: {email}")

        if _send_email(payload):
            summary["emails_sent"] += 1
            print(f"[{idx}] ✅ Sent -> {email}")
        else:
            summary["errors"].append(f"send_fail:{email}")
            print(f"[{idx}] ❌ Fail -> {email}")

    print(
        f"[Outreach Summary] targeted={summary['contacts_targeted']} "
        f"attempted={summary['emails_attempted']} sent={summary['emails_sent']} "
        f"errors={len(summary['errors'])}"
    )
    return summary

# Main entry
async def main():
    await connect_to_mongo()
    try:
        await send_outreach_emails([])
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
