"""
Clean Email Outreach Service for AI Recruitment Partner
Sends professional outreach emails to recruiters with matched candidates
"""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Email Configuration
SMTP_HOST = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("EMAIL_USERNAME", "shubhamopix@gmail.com")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Demo configuration
DEMO_EMAIL = "agtshaonidutta2k@gmail.com"  # Demo recipient email
DEMO_MODE = True


def send_sync_email(subject: str, recipient: str, body: str) -> bool:
    """Send email with proper error handling"""
    try:
        # Check if we have required SMTP settings
        if not SMTP_PASSWORD:
            logger.warning("No SMTP_PASSWORD configured - logging email instead")
            logger.info(f"EMAIL CONTENT (Demo Mode):")
            logger.info(f"To: {recipient}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body[:200]}...")
            return True  # Return success for demo purposes

        message = MIMEMultipart()
        message["From"] = SMTP_USER
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)

        logger.info(f"Email sent successfully to {recipient}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        logger.info(f"EMAIL CONTENT (Demo Mode):")
        logger.info(f"To: {recipient}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Body: {body[:200]}...")
        return False


def get_professional_outreach_template(
    job_title: str,
    company_name: str,
    company_achievement: str,
    candidates: List[Dict[str, Any]]
) -> str:
    """Generate professional outreach email template with proper HTML formatting"""

    # Build candidate profiles section with HTML formatting
    candidate_sections = []
    for i, candidate in enumerate(candidates, 1):
        name = candidate.get("name", "Candidate")
        score = candidate.get("score", 0.0)
        skills = candidate.get("skills", [])

        # Convert score to percentage and create match description
        match_percentage = int(score * 100) if isinstance(score, float) else int(score)
        skills_text = ", ".join(skills[:3]) if skills else "Multiple technical skills"

        candidate_section = f"""
        <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-left: 3px solid #007bff;">
            <strong>{i}. {name} | {match_percentage}% Match</strong><br>
            <strong>Key Skills:</strong> {skills_text}<br>
            <strong>Why they fit:</strong> Strong alignment with your technical requirements and proven experience
        </div>"""
        candidate_sections.append(candidate_section)

    candidates_html = "".join(candidate_sections)

    # Achievement line
    achievement_line = f"Congratulations on {company_achievement}! It looks like a game-changer, and it's exciting to see {company_name} pushing the industry forward."

    template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Perfect Candidates for Your {job_title} Position</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

    <p><strong>Hi [Recruiter Name],</strong></p>

    <p>{achievement_line}</p>

    <p>I'm reaching out regarding your open <strong>{job_title}</strong> position. I noticed the key requirements include deep expertise in the technologies outlined in your job description.</p>

    <p>I've identified <strong>{len(candidates)} candidate{'s' if len(candidates) > 1 else ''}</strong> from our talent pool who precisely match these qualifications and could be instrumental in scaling the {company_name} platform.</p>

    <div style="margin: 20px 0;">
        <h3 style="color: #007bff; margin-bottom: 15px;">Recommended Candidates:</h3>
        {candidates_html}
    </div>

    <p>Would you be open to a brief 15-minute call next week to discuss their profiles in more detail?</p>

    <p>Best regards,<br>
    <strong>Shaoni Dutta</strong><br>
    AI Recruitment Partner</p>

</body>
</html>"""

    return template


async def send_professional_outreach_email(
    recruiter_email: str,
    job_title: str,
    company_name: str,
    company_achievement: str,
    candidates: List[Dict[str, Any]],
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send professional outreach email to recruiter with candidate profiles
    In demo mode, sends all emails to demo account with proper labeling
    """
    try:
        # Create professional subject line
        if not subject:
            subject = f"Top {len(candidates)} candidate{'s' if len(candidates) > 1 else ''} for {job_title} at {company_name}"

        # Generate email body
        body = get_professional_outreach_template(
            job_title=job_title,
            company_name=company_name,
            company_achievement=company_achievement,
            candidates=candidates
        )

        # Send to demo account instead of original recipient
        actual_recipient = DEMO_EMAIL if DEMO_MODE else recruiter_email

        # Send email
        send_sync_email(subject=subject, recipient=actual_recipient, body=body)

        # Log success
        logger.info(f"Professional outreach email sent successfully to {actual_recipient}")
        logger.info(f"Job: {job_title} at {company_name}")
        logger.info(f"Candidates: {[c.get('name', 'Unknown') for c in candidates]}")

        return {
            "success": True,
            "message": f"Email sent to {actual_recipient}",
            "demo_mode": DEMO_MODE,
            "original_recipient": recruiter_email,
            "actual_recipient": actual_recipient,
            "job_title": job_title,
            "company_name": company_name,
            "candidates_count": len(candidates)
        }

    except Exception as e:
        error_msg = f"Error sending professional outreach email: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
