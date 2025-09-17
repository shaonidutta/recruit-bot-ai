"""
LLM-Powered Email Generation Service
Generates personalized, professional outreach emails using Google Gemini (Free)
"""

import os
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import asyncio

# Gemini imports (Primary and Only LLM)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    logging.warning("Google Generative AI not installed. Install with: pip install google-generativeai")

load_dotenv()
logger = logging.getLogger(__name__)

class LLMEmailService:
    """Service for generating personalized recruitment emails using Google Gemini (Free)"""

    def __init__(self):
        # Gemini Configuration (Only LLM)
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        # Configure Gemini
        if self.gemini_api_key and GEMINI_AVAILABLE and genai:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_client = genai.GenerativeModel(self.gemini_model)
            self.enabled = True
            logger.info(f"✅ Gemini configured: {self.gemini_model} (Free)")
        else:
            logger.error("❌ Gemini not configured - missing API key or installation")
            self.enabled = False
            self.gemini_client = None
        
    async def generate_personalized_outreach_email(
        self,
        job_details: Dict[str, Any],
        company_info: Dict[str, Any],
        matched_candidate: Optional[Dict[str, Any]] = None,
        email_type: str = "candidate_presentation",
        tone: str = "professional_warm",
        recruiter_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized outreach email using LLM with candidate information

        Args:
            job_details: Job information (title, description, requirements)
            company_info: Company information (name, industry, size, achievements)
            matched_candidate: Candidate information (name, skills, experience, score)
            email_type: Type of email (candidate_presentation, talent_partnership, cold_outreach)
            tone: Email tone (professional_warm, professional_formal, casual_friendly)
            recruiter_name: Recruiter's name if known

        Returns:
            Dict with generated email content, subject, and metadata
        """
        try:
            if not self.enabled:
                logger.warning("⚠️ Gemini not enabled, using fallback template")
                return self._generate_fallback_email(job_details, company_info, "Hiring Manager", matched_candidate)

            # Build context for Gemini with candidate information
            context = self._build_email_context(
                job_details, company_info, matched_candidate, email_type, tone, recruiter_name
            )

            # Generate email using Gemini
            response = await self._generate_with_gemini(context, email_type, tone)

            # Parse and validate response
            if response and "subject" in response and "body_html" in response:
                # Add metadata
                response.update({
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "model_used": self.gemini_model,
                    "llm_provider": "gemini",
                    "email_type": email_type,
                    "tone": tone,
                    "job_title": job_details.get("title"),
                    "company_name": company_info.get("name"),
                    "cost": "free"  # Gemini is free
                })

                logger.info(f"✅ Generated {email_type} email using Gemini for {company_info.get('name')} - {job_details.get('title')}")
                return response
            else:
                raise ValueError("Invalid Gemini response format")

        except Exception as e:
            logger.error(f"❌ Failed to generate email with Gemini: {e}")
            # Fallback to template-based generation
            return self._generate_fallback_email(job_details, company_info, "Hiring Manager", matched_candidate)

    async def _generate_with_gemini(self, context: str, email_type: str, tone: str) -> Dict[str, Any]:
        """Generate email using Google Gemini (Free)"""
        try:
            system_prompt = self._get_system_prompt(email_type, tone)
            full_prompt = f"{system_prompt}\n\n{context}"

            logger.info(f"🤖 Generating email with Gemini {self.gemini_model}...")

            # Generate with Gemini
            if not self.gemini_client:
                raise ValueError("Gemini client not initialized")

            # Create generation config
            generation_config = None
            if genai and hasattr(genai, 'GenerationConfig'):
                generation_config = genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                    response_mime_type="application/json"
                )

            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                full_prompt,
                generation_config=generation_config
            )

            # Parse JSON response
            email_data = json.loads(response.text)
            logger.info(f"✅ Gemini generated email successfully")
            return email_data

        except json.JSONDecodeError as e:
            logger.error(f"❌ Gemini returned invalid JSON: {e}")
            logger.error(f"Raw response: {response.text[:500]}...")
            raise
        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise

    def _build_email_context(
        self,
        job_details: Dict[str, Any],
        company_info: Dict[str, Any],
        matched_candidate: Optional[Dict[str, Any]],
        email_type: str,
        tone: str,
        recruiter_name: Optional[str]
    ) -> str:
        """Build context string for LLM email generation with candidate personalization"""

        # Extract candidate information if available
        candidate_name = "a qualified candidate"
        candidate_skills = []
        candidate_experience = "relevant"
        candidate_score = 0.0

        if matched_candidate:
            candidate_name = matched_candidate.get('candidate_name', 'a qualified candidate')
            candidate_skills = matched_candidate.get('candidate_skills', [])
            candidate_experience = f"{matched_candidate.get('candidate_experience', 0)} years"
            candidate_score = matched_candidate.get('score', 0.0)

        context = f"""
        Generate a concise, professional recruitment email presenting a specific candidate to a hiring manager.

        **Job Information:**
        - Title: {job_details.get('title', 'Software Engineer')}
        - Company: {company_info.get('name', 'Tech Company')}
        - Location: {job_details.get('location', 'Remote/Hybrid')}
        - Key Requirements: {', '.join(job_details.get('technical_skills', ['Python', 'React', 'AWS'])[:5])}
        - Experience Level: {job_details.get('experience_years_required', 'Mid-level')} years

        **Company Information:**
        - Industry: {company_info.get('industry', 'Technology')}
        - Size: {company_info.get('employee_count', 'Growing startup')} employees
        - Description: {company_info.get('description', 'Innovative technology company')}

        **Candidate Information:**
        - Name: {candidate_name}
        - Experience: {candidate_experience}
        - Key Skills: {', '.join(candidate_skills[:3]) if candidate_skills else 'Technical expertise'}
        - Match Score: {candidate_score:.1%} alignment with your requirements

        **Email Parameters:**
        - Type: {email_type}
        - Tone: {tone}
        - Recruiter Name: {recruiter_name or '[Hiring Manager]'}

        **Context:**
        I am Shaoni Dutta, an AI recruitment specialist. I've identified {candidate_name} as an excellent match for your {job_details.get('title', 'position')} role through our AI-powered matching system.

        **Critical Requirements:**
        1. MUST mention the candidate by name ({candidate_name})
        2. Keep email under 150 words (3-4 short paragraphs max)
        3. Lead with value proposition (qualified candidate for their specific role)
        4. Include relevant qualifications that match job requirements
        5. Professional, confident tone without being pushy
        6. Clear call-to-action (request for interview/discussion)
        7. Standard business email formatting
        8. Focus on candidate's fit for THIS specific role
        """
        
        return context
    
    def _get_system_prompt(self, email_type: str, tone: str) -> str:
        """Get system prompt based on email type and tone"""

        base_prompt = """
        You are an expert recruitment copywriter specializing in candidate presentation emails to hiring managers.
        Generate professional, concise recruitment emails that:

        1. Present a specific candidate by name to a hiring manager
        2. Are extremely concise (under 150 words, 3-4 short paragraphs max)
        3. Lead with value proposition (qualified candidate for their specific role)
        4. Include relevant candidate qualifications matching job requirements
        5. Use professional, confident tone without being pushy
        6. Include clear call-to-action (request for interview/discussion)
        7. Follow standard business email formatting
        8. Sound authentic and human-written (not AI-generated)

        Return response as JSON with these fields:
        {
            "subject": "Concise subject line with candidate name and role",
            "body_html": "HTML formatted email body (under 150 words)",
            "body_text": "Plain text version",
            "call_to_action": "Main CTA text",
            "personalization_elements": ["candidate_name", "job_title", "company_name", "key_skills"]
        }
        """

        tone_adjustments = {
            "professional_warm": "Use warm but professional language. Be approachable yet credible.",
            "professional_formal": "Use formal business language. Be direct and authoritative.",
            "casual_friendly": "Use friendly, conversational tone. Be personable and relatable."
        }

        email_type_adjustments = {
            "candidate_presentation": "Focus on presenting the candidate as an ideal fit for the specific role.",
            "talent_partnership": "Focus on long-term partnership and mutual value creation.",
            "cold_outreach": "Focus on immediate value and credibility building.",
            "warm_intro": "Reference mutual connections or previous interactions."
        }
        
        return f"""
        {base_prompt}
        
        **Tone Adjustment:** {tone_adjustments.get(tone, '')}
        **Email Type Focus:** {email_type_adjustments.get(email_type, '')}
        """
    
    def _generate_fallback_email(
        self,
        job_details: Dict[str, Any],
        company_info: Dict[str, Any],
        recruiter_name: Optional[str],
        matched_candidate: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate fallback email if LLM fails - now with candidate personalization"""

        company_name = company_info.get('name', 'your company')
        job_title = job_details.get('title', 'this position')

        # Extract candidate information
        candidate_name = "a qualified candidate"
        candidate_skills = "relevant technical skills"
        candidate_experience = "appropriate experience"

        if matched_candidate:
            candidate_name = matched_candidate.get('candidate_name', 'a qualified candidate')
            skills_list = matched_candidate.get('candidate_skills', [])
            candidate_skills = ', '.join(skills_list[:2]) if skills_list else "relevant technical skills"
            exp_years = matched_candidate.get('candidate_experience', 0)
            candidate_experience = f"{exp_years} years of experience" if exp_years else "appropriate experience"

        subject = f"Qualified Candidate: {candidate_name} for {job_title} at {company_name}"

        body_html = f"""
        <p>Hi {recruiter_name or 'there'},</p>

        <p>I'm Shaoni Dutta, and I'd like to present <strong>{candidate_name}</strong> for your <strong>{job_title}</strong> position.
        Through our AI matching system, they scored as an excellent fit for your requirements.</p>

        <p><strong>{candidate_name}</strong> brings {candidate_experience} with expertise in {candidate_skills},
        directly aligning with the technical needs outlined in your job posting.</p>

        <p>Would you be available for a brief call to discuss {candidate_name}'s qualifications and potential fit for your team?</p>

        <p>Best regards,<br>
        <strong>Shaoni Dutta</strong><br>
        AI Recruitment Specialist</p>
        """

        return {
            "subject": subject,
            "body_html": body_html,
            "body_text": body_html.replace('<p>', '').replace('</p>', '\n').replace('<strong>', '').replace('</strong>', '').replace('<br>', '\n'),
            "call_to_action": "Schedule a call to discuss the candidate",
            "personalization_elements": [candidate_name, company_name, job_title, candidate_skills],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model_used": "fallback_template",
            "email_type": "candidate_presentation",
            "tone": "professional_warm"
        }
    
    async def generate_multiple_variants(
        self,
        job_details: Dict[str, Any],
        company_info: Dict[str, Any],
        variant_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate multiple email variants for A/B testing"""
        
        variants = []
        email_types = ["talent_partnership", "cold_outreach", "warm_intro"]
        tones = ["professional_warm", "professional_formal", "casual_friendly"]
        
        for i in range(variant_count):
            email_type = email_types[i % len(email_types)]
            tone = tones[i % len(tones)]
            
            variant = await self.generate_personalized_outreach_email(
                job_details=job_details,
                company_info=company_info,
                email_type=email_type,
                tone=tone
            )
            
            variant["variant_id"] = f"variant_{i+1}"
            variants.append(variant)
        
        return variants

# Global service instance
llm_email_service = LLMEmailService()
