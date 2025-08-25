from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import os
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()


SMTP_HOST = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = "abhijeet.kr.chaurasiya@gmail.com"  # Fixed sender email
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD")


# async def send_email(
#     subject: str,
#     recipient: str,
#     body: str,
# ):
#     message = MIMEMultipart()
#     message["From"] = SMTP_USER
#     message["To"] = recipient
#     message["Subject"] = subject

#     message.attach(MIMEText(body, "html"))

#     await aiosmtplib.send(
#         message,
#         hostname=SMTP_HOST,
#         port=SMTP_PORT,
#         username=SMTP_USER,
#         password=SMTP_PASSWORD,
#         start_tls=True,
#     )


def send_sync_email(
    subject: str,
    recipient: str,
    body: str,
):
    message = MIMEMultipart()
    message["From"] = SMTP_USER
    message["To"] = recipient
    message["Subject"] = subject

    message.attach(MIMEText(body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)


def test_email_sending(recipient_email: str):
    """
    Test function to verify email sending functionality
    """
    subject = "Test Email from AI Recruitment Agent"
    body = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Hello World!</h1>
        <p>This is a test email from AI Recruitment Agent system.</p>
        <p>If you received this email, the email service is working correctly.</p>
    </body>
    </html>
    """

    try:
        send_sync_email(subject=subject, recipient=recipient_email, body=body)
        logger.info(f"✅ Test email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Error sending test email: {str(e)}")
        return False


def get_professional_outreach_template(
    job_title: str,
    company_name: str,
    company_achievement: str,
    candidates: list
) -> str:
    """Generate professional outreach email template matching the user's exact format"""
    
    # Build candidate profiles section
    candidate_sections = []
    for i, candidate in enumerate(candidates, 1):
        name = candidate.get("name", "Candidate")
        title = candidate.get("title", "Developer")
        expertise = candidate.get("expertise", "Strong technical background")
        why_fit = candidate.get("why_fit", "Great match for your requirements")
        
        candidate_section = f"""{i}. {name} | {title}
Expertise: {expertise}
Why they fit: {why_fit}"""
        candidate_sections.append(candidate_section)
    
    candidates_text = "\n\n".join(candidate_sections)
    
    # Achievement line
    achievement_line = f"Congratulations on {company_achievement}! It looks like a game-changer, and it's exciting to see {company_name} pushing the industry forward."
    
    template = f"""Hi [Recruiter Name],

{achievement_line}

I'm reaching out regarding your open {job_title} position. I noticed the key requirements include deep expertise in the technologies outlined in your job description.

I've identified {len(candidates)} candidate{'s' if len(candidates) > 1 else ''} from our talent pool who precisely match these qualifications and could be instrumental in scaling the {company_name} platform.

{candidates_text}

Would you be open to a brief 15-minute call next week to discuss their profiles in more detail?

Best regards,
Abhijeet Kumar Chaurasiya
AI Recruitment Partner"""
    
    return template


async def send_job_match_email(
    candidate_id: str,
    job_id: str,
    recipient_email: str,
    match_score: float,
    dashboard_link: str = None,
) -> Dict[str, Any]:
    """
    Send a job match notification email to the candidate
    """
    try:
        # Get database connection
        database = await get_database()
        
        # Get candidate data
        candidate_collection = database.get_collection("candidates")
        candidate = await candidate_collection.find_one({"_id": ObjectId(candidate_id)})
        
        if not candidate:
            logger.error(f"Candidate not found: {candidate_id}")
            return False
        
        # Get job data
        job_collection = database.get_collection("jobs")
        job = await job_collection.find_one({"_id": ObjectId(job_id)})
        
        
        if not job:
            logger.error(f"Job not found: {job_id}")
            return False
        
        candidate_name = candidate.get("name", candidate.get("email", "Candidate"))
        job_title = job.get("title", "Position")
        company_name = job.get("company", "Company")
        job_url = job.get("url", "#")
        
        # Generate email content
        subject = f"🎯 Perfect Job Match: {job_title} at {company_name}"
        body = get_job_match_email_template(
            candidate_name=candidate_name,
            job_title=job_title,
            company_name=company_name,
            match_score=match_score,
            job_url=job_url,
            dashboard_link=dashboard_link,
        )
        
        # Send email
        send_sync_email(subject=subject, recipient=recipient_email, body=body)
        
        logger.info(f"Job match email sent successfully to {recipient_email} for job {job_id}")
        return True
        
    except Exception as e:
         logger.error(f"Error sending job match email: {str(e)}")
         return False


async def send_candidate_outreach_email(
    candidate_email: str,
    candidate_name: str,
    subject: str = None,
    custom_message: str = None,
) -> bool:
    """
    Send a general outreach email to a candidate
    """
    try:
        if not subject:
            subject = "Exciting Career Opportunities Await You!"
        
        if not custom_message:
            custom_message = "We have some exciting job opportunities that might be perfect for you."
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Career Opportunity</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f7fa;">
            <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 300; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        🚀 Career Opportunities
                    </h1>
                </div>
                
                <div style="padding: 40px 30px;">
                    <h2 style="color: #2c3e50; font-size: 24px; font-weight: 400; margin: 0 0 20px 0; line-height: 1.4;">
                        Hello {candidate_name},
                    </h2>
                    
                    <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                        {custom_message}
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 30px 0; border-radius: 0 8px 8px 0;">
                        <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">
                            💡 <strong>Why choose us?</strong> We use AI-powered matching to find opportunities that truly align with your skills and career goals.
                        </p>
                    </div>
                    
                    <p style="color: #5a6c7d; font-size: 16px; line-height: 1.6; margin: 25px 0 0 0;">
                        Best regards,<br>
                        <strong>AI Recruitment Agent Team</strong>
                    </p>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px 30px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="margin: 0; font-size: 12px; color: #6c757d; line-height: 1.4;">
                        This is an automated email from <strong>AI Recruitment Agent</strong><br>
                        <span style="color: #adb5bd;">© 2025 AI Recruitment Agent. All rights reserved.</span>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_sync_email(subject=subject, recipient=candidate_email, body=body)
        logger.info(f"Outreach email sent successfully to {candidate_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending outreach email: {str(e)}")
        return False


async def send_professional_outreach_email(
    recruiter_email: str,
    job_title: str,
    company_name: str,
    company_achievement: str,
    candidates: List[Dict[str, Any]],
    subject: str = None
) -> Dict[str, Any]:
    """
    Send professional outreach email to recruiter with candidate profiles
    """
    try:
        if not subject:
            subject = f"Top {len(candidates)} candidate{'s' if len(candidates) > 1 else ''} for {job_title} at {company_name}"
        
        body = get_professional_outreach_template(
            job_title=job_title,
            company_name=company_name,
            company_achievement=company_achievement,
            candidates=candidates
        )
        
        send_sync_email(subject=subject, recipient=recruiter_email, body=body)
        logger.info(f"Professional outreach email sent successfully to {recruiter_email}")
        return {"success": True, "message": f"Email sent to {recruiter_email}"}
        
    except Exception as e:
        error_msg = f"Error sending professional outreach email: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


async def send_outreach_emails(
    candidates: list,
    subject: str = None,
    custom_message: str = None,
) -> dict:
    """
    Send outreach emails to multiple candidates
    
    Args:
        candidates: List of candidate dictionaries with 'email' and 'name' fields
        subject: Email subject (optional, uses default if not provided)
        custom_message: Custom message to include in the email
    
    Returns:
        dict: Summary of email sending results
    """
    results = {
        "total_candidates": len(candidates),
        "emails_sent": 0,
        "emails_failed": 0,
        "failed_emails": []
    }
    
    logger.info(f"Starting bulk email outreach to {len(candidates)} candidates")
    
    for candidate in candidates:
        try:
            candidate_email = candidate.get('email')
            candidate_name = candidate.get('name', 'Candidate')
            
            if not candidate_email:
                logger.warning(f"Skipping candidate with missing email: {candidate}")
                results["emails_failed"] += 1
                results["failed_emails"].append({"candidate": candidate, "reason": "Missing email"})
                continue
            
            success = await send_candidate_outreach_email(
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                subject=subject,
                custom_message=custom_message
            )
            
            if success:
                results["emails_sent"] += 1
            else:
                results["emails_failed"] += 1
                results["failed_emails"].append({"candidate": candidate, "reason": "Send failed"})
                
        except Exception as e:
            logger.error(f"Error processing candidate {candidate}: {str(e)}")
            results["emails_failed"] += 1
            results["failed_emails"].append({"candidate": candidate, "reason": str(e)})
    
    logger.info(f"Bulk email outreach completed. Sent: {results['emails_sent']}, Failed: {results['emails_failed']}")
    return results


# Example usage function
if __name__ == "__main__":
    # Test the email service
    test_email = "test@example.com"
    print(f"Testing email service with {test_email}...")
    test_email_sending(test_email)