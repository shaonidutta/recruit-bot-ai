import openai
import asyncio
import logging
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime
from ..models import JobPosting, Candidate, Contact, CompanyInfo, OutreachTemplate, OutreachCampaign
from ..common.utils import extract_skills_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerationService:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Template categories
        self.template_types = {
            'initial_outreach': 'First contact email to hiring manager',
            'follow_up': 'Follow-up email after no response',
            'linkedin_message': 'LinkedIn connection request message',
            'linkedin_follow_up': 'LinkedIn follow-up message',
            'thank_you': 'Thank you email after interview',
            'application_submission': 'Email when submitting application'
        }
        
        # Tone variations for A/B testing
        self.tone_variations = {
            'professional': 'Professional and formal tone',
            'friendly': 'Warm and friendly tone',
            'confident': 'Confident and assertive tone',
            'casual': 'Casual and conversational tone',
            'enthusiastic': 'Enthusiastic and energetic tone'
        }
        
    async def generate_personalized_email(self, 
                                         candidate: Candidate, 
                                         job: JobPosting, 
                                         contact: Contact = None,
                                         company_info: CompanyInfo = None,
                                         template_type: str = 'initial_outreach',
                                         tone: str = 'professional') -> OutreachTemplate:
        """
        Generate a personalized email template using GPT-4
        """
        try:
            # Gather context for personalization
            context = self._build_context(candidate, job, contact, company_info)
            
            # Generate subject line
            subject = await self._generate_subject_line(context, template_type, tone)
            
            # Generate email body
            body = await self._generate_email_body(context, template_type, tone)
            
            # Generate call-to-action
            cta = await self._generate_call_to_action(context, template_type)
            
            return OutreachTemplate(
                template_id=f"{template_type}_{tone}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                template_type=template_type,
                subject_line=subject,
                email_body=body,
                call_to_action=cta,
                tone=tone,
                personalization_data=context,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating personalized email: {str(e)}")
            return self._create_fallback_template(template_type, tone)
    
    async def generate_linkedin_message(self,
                                      candidate: Candidate,
                                      job: JobPosting,
                                      contact: Contact = None,
                                      company_info: CompanyInfo = None,
                                      message_type: str = 'connection_request') -> str:
        """
        Generate a personalized LinkedIn message
        """
        try:
            context = self._build_context(candidate, job, contact, company_info)
            
            prompt = self._build_linkedin_prompt(context, message_type)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert recruiter and career coach who writes compelling, personalized LinkedIn messages that get responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            
            # Ensure LinkedIn character limits
            if message_type == 'connection_request' and len(message) > 300:
                message = message[:297] + "..."
            elif len(message) > 8000:  # LinkedIn message limit
                message = message[:7997] + "..."
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {str(e)}")
            return self._create_fallback_linkedin_message(message_type)
    
    async def generate_multiple_variations(self,
                                         candidate: Candidate,
                                         job: JobPosting,
                                         contact: Contact = None,
                                         company_info: CompanyInfo = None,
                                         template_type: str = 'initial_outreach',
                                         num_variations: int = 3) -> List[OutreachTemplate]:
        """
        Generate multiple variations for A/B testing
        """
        variations = []
        tones = list(self.tone_variations.keys())[:num_variations]
        
        for tone in tones:
            template = await self.generate_personalized_email(
                candidate, job, contact, company_info, template_type, tone
            )
            variations.append(template)
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return variations
    
    async def generate_follow_up_sequence(self,
                                        candidate: Candidate,
                                        job: JobPosting,
                                        contact: Contact = None,
                                        company_info: CompanyInfo = None,
                                        sequence_length: int = 3) -> List[OutreachTemplate]:
        """
        Generate a sequence of follow-up emails
        """
        sequence = []
        
        # Initial outreach
        initial = await self.generate_personalized_email(
            candidate, job, contact, company_info, 'initial_outreach'
        )
        sequence.append(initial)
        
        # Follow-up emails
        for i in range(1, sequence_length):
            follow_up = await self.generate_personalized_email(
                candidate, job, contact, company_info, 'follow_up'
            )
            # Modify template_id to indicate sequence position
            follow_up.template_id += f"_seq_{i+1}"
            sequence.append(follow_up)
            
            await asyncio.sleep(0.5)
        
        return sequence
    
    def _build_context(self, 
                      candidate: Candidate, 
                      job: JobPosting, 
                      contact: Contact = None,
                      company_info: CompanyInfo = None) -> Dict[str, Any]:
        """
        Build context for personalization
        """
        context = {
            'candidate_name': candidate.name,
            'candidate_skills': candidate.skills,
            'candidate_experience': candidate.experience_years,
            'candidate_current_role': getattr(candidate, 'current_role', ''),
            'job_title': job.title,
            'company_name': job.company,
            'job_location': job.location,
            'job_description': job.description[:500],  # Truncate for context
            'job_requirements': extract_skills_from_text(job.description)[:5],  # Top 5 skills
        }
        
        if contact:
            context.update({
                'contact_name': contact.name,
                'contact_title': contact.title,
                'contact_first_name': contact.name.split()[0] if contact.name else 'Hiring Manager'
            })
        
        if company_info:
            context.update({
                'company_industry': company_info.industry,
                'company_size': company_info.size,
                'company_description': company_info.description[:200],
                'company_technologies': company_info.technologies[:3]  # Top 3 technologies
            })
        
        return context
    
    async def _generate_subject_line(self, context: Dict[str, Any], template_type: str, tone: str) -> str:
        """
        Generate personalized subject line
        """
        prompt = f"""
        Generate a compelling email subject line for a {template_type} email.
        
        Context:
        - Candidate: {context['candidate_name']}
        - Job: {context['job_title']} at {context['company_name']}
        - Tone: {tone}
        
        Requirements:
        - Maximum 50 characters
        - Personalized and attention-grabbing
        - Professional but engaging
        - Avoid spam trigger words
        
        Generate only the subject line, no quotes or extra text.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert email marketer who writes high-converting subject lines."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.8
            )
            
            subject = response.choices[0].message.content.strip()
            return subject[:50]  # Ensure character limit
            
        except Exception as e:
            logger.error(f"Error generating subject line: {str(e)}")
            return f"Opportunity: {context['job_title']} at {context['company_name']}"
    
    async def _generate_email_body(self, context: Dict[str, Any], template_type: str, tone: str) -> str:
        """
        Generate personalized email body
        """
        prompt = f"""
        Write a personalized {template_type} email with a {tone} tone.
        
        Context:
        - Candidate: {context['candidate_name']}
        - Experience: {context['candidate_experience']} years
        - Skills: {', '.join(context['candidate_skills'][:5])}
        - Job: {context['job_title']} at {context['company_name']}
        - Location: {context['job_location']}
        - Contact: {context.get('contact_first_name', 'Hiring Manager')}
        
        Requirements:
        - 150-250 words
        - Highlight relevant skills and experience
        - Show genuine interest in the company/role
        - Include specific details from the job/company
        - End with a clear next step
        - Use proper email formatting
        
        Write the email body only, starting with the greeting.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert career coach who writes compelling, personalized outreach emails that get responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating email body: {str(e)}")
            return self._create_fallback_email_body(context, template_type)
    
    async def _generate_call_to_action(self, context: Dict[str, Any], template_type: str) -> str:
        """
        Generate appropriate call-to-action
        """
        cta_prompts = {
            'initial_outreach': "Request for a brief conversation or interview",
            'follow_up': "Gentle reminder and availability confirmation",
            'linkedin_message': "Request to connect and discuss opportunities",
            'application_submission': "Confirmation of application and next steps"
        }
        
        prompt = f"""
        Generate a compelling call-to-action for a {template_type} email.
        
        Context: {cta_prompts.get(template_type, 'Professional next step')}
        
        Requirements:
        - 1-2 sentences maximum
        - Clear and specific
        - Easy to respond to
        - Professional tone
        
        Generate only the call-to-action text.
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing compelling call-to-action statements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating CTA: {str(e)}")
            return "I'd love to discuss this opportunity further. Are you available for a brief call this week?"
    
    def _build_linkedin_prompt(self, context: Dict[str, Any], message_type: str) -> str:
        """
        Build prompt for LinkedIn message generation
        """
        if message_type == 'connection_request':
            return f"""
            Write a personalized LinkedIn connection request message.
            
            Context:
            - Candidate: {context['candidate_name']}
            - Job: {context['job_title']} at {context['company_name']}
            - Contact: {context.get('contact_first_name', 'Professional')}
            
            Requirements:
            - Maximum 300 characters (LinkedIn limit)
            - Mention the specific role
            - Professional but friendly
            - Clear reason for connecting
            
            Write only the message text.
            """
        else:
            return f"""
            Write a personalized LinkedIn follow-up message.
            
            Context:
            - Candidate: {context['candidate_name']}
            - Job: {context['job_title']} at {context['company_name']}
            - Contact: {context.get('contact_first_name', 'Professional')}
            
            Requirements:
            - 100-200 words
            - Reference previous connection
            - Highlight relevant qualifications
            - Include clear next step
            
            Write only the message text.
            """
    
    def _create_fallback_template(self, template_type: str, tone: str) -> OutreachTemplate:
        """
        Create fallback template when GPT-4 fails
        """
        fallback_templates = {
            'initial_outreach': {
                'subject': "Interested in [Job Title] Opportunity",
                'body': """Dear Hiring Manager,

I hope this email finds you well. I am writing to express my strong interest in the [Job Title] position at [Company Name].

With [X] years of experience in [relevant field], I believe I would be a valuable addition to your team. My background in [key skills] aligns well with the requirements outlined in the job posting.

I would welcome the opportunity to discuss how my experience and passion for [industry/field] can contribute to [Company Name]'s continued success.

Thank you for your time and consideration.

Best regards,
[Candidate Name]""",
                'cta': "I would love to schedule a brief call to discuss this opportunity further."
            }
        }
        
        template_data = fallback_templates.get(template_type, fallback_templates['initial_outreach'])
        
        return OutreachTemplate(
            template_id=f"fallback_{template_type}_{tone}",
            template_type=template_type,
            subject_line=template_data['subject'],
            email_body=template_data['body'],
            call_to_action=template_data['cta'],
            tone=tone,
            personalization_data={},
            created_at=datetime.now()
        )
    
    def _create_fallback_email_body(self, context: Dict[str, Any], template_type: str) -> str:
        """
        Create fallback email body
        """
        contact_name = context.get('contact_first_name', 'Hiring Manager')
        
        return f"""Dear {contact_name},

I hope this email finds you well. I am writing to express my strong interest in the {context['job_title']} position at {context['company_name']}.

With {context['candidate_experience']} years of experience and expertise in {', '.join(context['candidate_skills'][:3])}, I believe I would be a valuable addition to your team. I am particularly drawn to this opportunity because of {context['company_name']}'s reputation in the industry.

I would welcome the opportunity to discuss how my background and passion for this field can contribute to your team's success.

Thank you for your time and consideration.

Best regards,
{context['candidate_name']}"""
    
    def _create_fallback_linkedin_message(self, message_type: str) -> str:
        """
        Create fallback LinkedIn message
        """
        if message_type == 'connection_request':
            return "Hi! I'm interested in opportunities at your company and would love to connect to learn more about your team."
        else:
            return "Thank you for connecting! I'm very interested in opportunities at your company and would love to learn more about potential openings that might be a good fit for my background."

# Global instance
content_service = ContentGenerationService()

def set_openai_api_key(api_key: str):
    """
    Set OpenAI API key for content generation
    """
    global content_service
    content_service.openai_api_key = api_key
    openai.api_key = api_key

async def generate_personalized_outreach(candidate: Candidate, 
                                       job: JobPosting, 
                                       contact: Contact = None,
                                       company_info: CompanyInfo = None,
                                       template_type: str = 'initial_outreach',
                                       tone: str = 'professional') -> OutreachTemplate:
    """
    Generate personalized outreach template
    """
    return await content_service.generate_personalized_email(
        candidate, job, contact, company_info, template_type, tone
    )

async def generate_linkedin_outreach(candidate: Candidate,
                                    job: JobPosting,
                                    contact: Contact = None,
                                    company_info: CompanyInfo = None,
                                    message_type: str = 'connection_request') -> str:
    """
    Generate LinkedIn message
    """
    return await content_service.generate_linkedin_message(
        candidate, job, contact, company_info, message_type
    )

async def generate_ab_test_variations(candidate: Candidate,
                                    job: JobPosting,
                                    contact: Contact = None,
                                    company_info: CompanyInfo = None,
                                    num_variations: int = 3) -> List[OutreachTemplate]:
    """
    Generate multiple variations for A/B testing
    """
    return await content_service.generate_multiple_variations(
        candidate, job, contact, company_info, 'initial_outreach', num_variations
    )

async def generate_email_sequence(candidate: Candidate,
                                 job: JobPosting,
                                 contact: Contact = None,
                                 company_info: CompanyInfo = None,
                                 sequence_length: int = 3) -> List[OutreachTemplate]:
    """
    Generate follow-up email sequence
    """
    return await content_service.generate_follow_up_sequence(
        candidate, job, contact, company_info, sequence_length
    )