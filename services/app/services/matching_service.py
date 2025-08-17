import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz, process
import re
from ..models import JobPosting, Candidate, JobMatch, MatchScore, ParsedJobData
from ..common.utils import calculate_text_similarity, extract_skills_from_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMatchingEngine:
    def __init__(self):
        self.skill_weights = {
            'programming_languages': 0.25,
            'frameworks': 0.20,
            'tools': 0.15,
            'databases': 0.15,
            'soft_skills': 0.10,
            'certifications': 0.10,
            'domain_knowledge': 0.05
        }
        
        self.experience_levels = {
            'entry': (0, 2),
            'junior': (1, 3),
            'mid': (3, 6),
            'senior': (5, 10),
            'lead': (7, 15),
            'principal': (10, 20),
            'executive': (15, 30)
        }
        
        # Initialize TF-IDF vectorizer for text similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
    def calculate_job_match(self, candidate: Candidate, job: JobPosting, parsed_job: ParsedJobData = None) -> JobMatch:
        """
        Calculate comprehensive match score between candidate and job
        """
        try:
            # Use parsed job data if available, otherwise use original job posting
            job_data = parsed_job if parsed_job else job
            
            # Calculate individual match scores
            skills_score = self._calculate_skills_match(candidate, job_data)
            experience_score = self._calculate_experience_match(candidate, job_data)
            location_score = self._calculate_location_match(candidate, job)
            salary_score = self._calculate_salary_match(candidate, job_data)
            culture_score = self._calculate_culture_match(candidate, job_data)
            
            # Calculate overall weighted score
            overall_score = (
                skills_score * 0.35 +
                experience_score * 0.25 +
                location_score * 0.15 +
                salary_score * 0.15 +
                culture_score * 0.10
            )
            
            # Create match score object
            match_score = MatchScore(
                overall_score=round(overall_score, 2),
                skills_match=round(skills_score, 2),
                experience_match=round(experience_score, 2),
                location_match=round(location_score, 2),
                salary_match=round(salary_score, 2),
                culture_match=round(culture_score, 2)
            )
            
            # Identify matched and missing skills
            matched_skills, missing_skills = self._analyze_skill_gaps(candidate, job_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(candidate, job_data, match_score)
            
            return JobMatch(
                job_id=job.id or f"job_{hash(job.title + job.company)}",
                candidate_id=candidate.id or f"candidate_{hash(candidate.email)}",
                match_score=match_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error calculating job match: {str(e)}")
            return self._create_fallback_match(candidate, job)
    
    def _calculate_skills_match(self, candidate: Candidate, job_data) -> float:
        """
        Calculate skills compatibility score
        """
        try:
            candidate_skills = [skill.lower().strip() for skill in candidate.skills]
            
            # Get job skills from different sources
            job_skills = []
            if hasattr(job_data, 'technical_skills'):
                job_skills.extend([skill.lower().strip() for skill in job_data.technical_skills])
            if hasattr(job_data, 'skills_required'):
                job_skills.extend([skill.lower().strip() for skill in job_data.skills_required])
            
            # Extract skills from job description if not available
            if not job_skills and hasattr(job_data, 'description'):
                extracted_skills = extract_skills_from_text(job_data.description)
                job_skills = [skill.lower().strip() for skill in extracted_skills]
            
            if not job_skills or not candidate_skills:
                return 50.0  # Neutral score when skills data is missing
            
            # Calculate exact matches
            exact_matches = len(set(candidate_skills) & set(job_skills))
            
            # Calculate fuzzy matches for similar skills
            fuzzy_matches = 0
            for candidate_skill in candidate_skills:
                if candidate_skill not in job_skills:
                    best_match = process.extractOne(candidate_skill, job_skills)
                    if best_match and best_match[1] >= 80:  # 80% similarity threshold
                        fuzzy_matches += 0.8  # Partial credit for fuzzy matches
            
            total_matches = exact_matches + fuzzy_matches
            skills_score = min(100, (total_matches / len(job_skills)) * 100)
            
            return skills_score
            
        except Exception as e:
            logger.error(f"Error calculating skills match: {str(e)}")
            return 50.0
    
    def _calculate_experience_match(self, candidate: Candidate, job_data) -> float:
        """
        Calculate experience level match
        """
        try:
            candidate_years = candidate.experience_years
            
            # Parse job experience requirements
            job_experience_text = getattr(job_data, 'experience_level', 'Not specified')
            if hasattr(job_data, 'description'):
                job_experience_text += " " + job_data.description
            
            # Extract years from job description
            required_years = self._extract_years_from_text(job_experience_text)
            
            if required_years is None:
                return 75.0  # Neutral score when experience requirements are unclear
            
            # Calculate experience match score
            if candidate_years >= required_years:
                # Candidate meets or exceeds requirements
                if candidate_years <= required_years + 3:
                    return 100.0  # Perfect match
                elif candidate_years <= required_years + 6:
                    return 90.0   # Slightly overqualified
                else:
                    return 75.0   # Significantly overqualified
            else:
                # Candidate has less experience than required
                gap = required_years - candidate_years
                if gap <= 1:
                    return 85.0   # Close enough
                elif gap <= 2:
                    return 70.0   # Moderate gap
                elif gap <= 3:
                    return 50.0   # Significant gap
                else:
                    return 25.0   # Large gap
                    
        except Exception as e:
            logger.error(f"Error calculating experience match: {str(e)}")
            return 50.0
    
    def _calculate_location_match(self, candidate: Candidate, job: JobPosting) -> float:
        """
        Calculate location compatibility score
        """
        try:
            job_location = job.location.lower().strip()
            candidate_location = candidate.current_location.lower().strip()
            preferred_locations = [loc.lower().strip() for loc in candidate.preferred_locations]
            
            # Check for remote work
            if job.remote_option or 'remote' in job_location:
                return 100.0
            
            # Check if job location matches candidate's current location
            if self._locations_match(job_location, candidate_location):
                return 100.0
            
            # Check if job location matches any preferred locations
            for pref_loc in preferred_locations:
                if self._locations_match(job_location, pref_loc):
                    return 95.0
            
            # Check for same city/state
            if self._same_city_or_state(job_location, candidate_location):
                return 80.0
            
            # Check for same country
            if self._same_country(job_location, candidate_location):
                return 60.0
            
            return 30.0  # Different countries
            
        except Exception as e:
            logger.error(f"Error calculating location match: {str(e)}")
            return 50.0
    
    def _calculate_salary_match(self, candidate: Candidate, job_data) -> float:
        """
        Calculate salary expectation match
        """
        try:
            if not candidate.salary_expectation:
                return 75.0  # Neutral score when candidate has no salary expectation
            
            # Extract salary from job
            job_salary_text = getattr(job_data, 'salary_info', 'Not specified')
            if job_salary_text == 'Not specified' and hasattr(job_data, 'salary_range'):
                job_salary_text = job_data.salary_range
            
            candidate_salary = self._extract_salary_from_text(candidate.salary_expectation)
            job_salary = self._extract_salary_from_text(job_salary_text)
            
            if not job_salary or not candidate_salary:
                return 75.0  # Neutral score when salary data is missing
            
            # Calculate salary match
            if job_salary >= candidate_salary:
                return 100.0  # Job meets or exceeds expectation
            else:
                gap_percentage = (candidate_salary - job_salary) / candidate_salary
                if gap_percentage <= 0.1:  # Within 10%
                    return 90.0
                elif gap_percentage <= 0.2:  # Within 20%
                    return 75.0
                elif gap_percentage <= 0.3:  # Within 30%
                    return 50.0
                else:
                    return 25.0  # Significant gap
                    
        except Exception as e:
            logger.error(f"Error calculating salary match: {str(e)}")
            return 50.0
    
    def _calculate_culture_match(self, candidate: Candidate, job_data) -> float:
        """
        Calculate culture fit score based on job description sentiment and keywords
        """
        try:
            # Get job description
            description = getattr(job_data, 'description', '')
            if not description:
                return 75.0
            
            # Analyze company culture indicators
            culture_score = 75.0  # Base score
            
            # Positive culture indicators
            positive_indicators = [
                'collaborative', 'team-oriented', 'innovative', 'flexible',
                'work-life balance', 'growth opportunities', 'learning',
                'inclusive', 'diverse', 'supportive', 'mentorship'
            ]
            
            # Negative culture indicators
            negative_indicators = [
                'high-pressure', 'fast-paced', 'demanding', 'strict deadlines',
                'long hours', 'overtime', 'stressful'
            ]
            
            description_lower = description.lower()
            
            # Boost score for positive indicators
            positive_count = sum(1 for indicator in positive_indicators if indicator in description_lower)
            culture_score += min(20, positive_count * 3)
            
            # Reduce score for negative indicators
            negative_count = sum(1 for indicator in negative_indicators if indicator in description_lower)
            culture_score -= min(25, negative_count * 5)
            
            # Use sentiment score if available
            if hasattr(job_data, 'sentiment_score'):
                sentiment = job_data.sentiment_score
                if sentiment > 0.1:
                    culture_score += 10
                elif sentiment < -0.1:
                    culture_score -= 10
            
            return max(0, min(100, culture_score))
            
        except Exception as e:
            logger.error(f"Error calculating culture match: {str(e)}")
            return 50.0
    
    def _analyze_skill_gaps(self, candidate: Candidate, job_data) -> Tuple[List[str], List[str]]:
        """
        Analyze matched and missing skills
        """
        try:
            candidate_skills = set(skill.lower().strip() for skill in candidate.skills)
            
            job_skills = set()
            if hasattr(job_data, 'technical_skills'):
                job_skills.update(skill.lower().strip() for skill in job_data.technical_skills)
            if hasattr(job_data, 'skills_required'):
                job_skills.update(skill.lower().strip() for skill in job_data.skills_required)
            
            matched_skills = list(candidate_skills & job_skills)
            missing_skills = list(job_skills - candidate_skills)
            
            return matched_skills, missing_skills
            
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {str(e)}")
            return [], []
    
    def _generate_recommendations(self, candidate: Candidate, job_data, match_score: MatchScore) -> List[str]:
        """
        Generate personalized recommendations for improving match
        """
        recommendations = []
        
        try:
            # Skills recommendations
            if match_score.skills_match < 70:
                _, missing_skills = self._analyze_skill_gaps(candidate, job_data)
                if missing_skills:
                    top_missing = missing_skills[:3]
                    recommendations.append(f"Consider learning: {', '.join(top_missing)}")
            
            # Experience recommendations
            if match_score.experience_match < 70:
                recommendations.append("Highlight relevant projects and achievements to demonstrate experience")
            
            # Location recommendations
            if match_score.location_match < 80:
                recommendations.append("Consider mentioning willingness to relocate or work remotely")
            
            # Salary recommendations
            if match_score.salary_match < 70:
                recommendations.append("Consider if salary expectations are flexible based on other benefits")
            
            # General recommendations based on overall score
            if match_score.overall_score >= 80:
                recommendations.append("Excellent match! Consider applying immediately.")
            elif match_score.overall_score >= 60:
                recommendations.append("Good match. Tailor your application to highlight relevant skills.")
            else:
                recommendations.append("Consider improving skills or gaining more experience before applying.")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Review job requirements and tailor your application accordingly."]
    
    def _extract_years_from_text(self, text: str) -> int:
        """
        Extract years of experience from text
        """
        if not text:
            return None
        
        # Common patterns for years of experience
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\+\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        
        # Check for experience level keywords
        text_lower = text.lower()
        for level, (min_years, max_years) in self.experience_levels.items():
            if level in text_lower:
                return min_years
        
        return None
    
    def _extract_salary_from_text(self, text: str) -> int:
        """
        Extract salary amount from text
        """
        if not text:
            return None
        
        # Remove common currency symbols and normalize
        text = re.sub(r'[,$]', '', text)
        
        # Look for salary patterns
        patterns = [
            r'(\d+)k',  # 100k format
            r'(\d{2,3})\s*thousand',  # 100 thousand
            r'(\d{4,6})',  # Direct number like 100000
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                amount = int(matches[0])
                if 'k' in text.lower() or 'thousand' in text.lower():
                    amount *= 1000
                return amount
        
        return None
    
    def _locations_match(self, loc1: str, loc2: str) -> bool:
        """
        Check if two locations match
        """
        return fuzz.ratio(loc1, loc2) >= 85
    
    def _same_city_or_state(self, loc1: str, loc2: str) -> bool:
        """
        Check if locations are in the same city or state
        """
        # Simple heuristic - check if they share common words
        words1 = set(loc1.split())
        words2 = set(loc2.split())
        common_words = words1 & words2
        return len(common_words) > 0
    
    def _same_country(self, loc1: str, loc2: str) -> bool:
        """
        Check if locations are in the same country
        """
        countries = ['usa', 'us', 'united states', 'canada', 'uk', 'united kingdom']
        
        loc1_country = None
        loc2_country = None
        
        for country in countries:
            if country in loc1:
                loc1_country = country
            if country in loc2:
                loc2_country = country
        
        return loc1_country == loc2_country if loc1_country and loc2_country else False
    
    def _create_fallback_match(self, candidate: Candidate, job: JobPosting) -> JobMatch:
        """
        Create a fallback match when calculation fails
        """
        fallback_score = MatchScore(
            overall_score=50.0,
            skills_match=50.0,
            experience_match=50.0,
            location_match=50.0,
            salary_match=50.0,
            culture_match=50.0
        )
        
        return JobMatch(
            job_id=job.id or f"job_{hash(job.title + job.company)}",
            candidate_id=candidate.id or f"candidate_{hash(candidate.email)}",
            match_score=fallback_score,
            matched_skills=[],
            missing_skills=[],
            recommendations=["Unable to calculate detailed match. Please review manually."]
        )
    
    def rank_jobs_for_candidate(self, candidate: Candidate, jobs: List[JobPosting], parsed_jobs: List[ParsedJobData] = None) -> List[JobMatch]:
        """
        Rank all jobs for a candidate and return sorted matches
        """
        matches = []
        
        for i, job in enumerate(jobs):
            parsed_job = parsed_jobs[i] if parsed_jobs and i < len(parsed_jobs) else None
            match = self.calculate_job_match(candidate, job, parsed_job)
            matches.append(match)
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        
        return matches
    
    def find_best_candidates_for_job(self, job: JobPosting, candidates: List[Candidate], parsed_job: ParsedJobData = None) -> List[JobMatch]:
        """
        Find and rank best candidates for a specific job
        """
        matches = []
        
        for candidate in candidates:
            match = self.calculate_job_match(candidate, job, parsed_job)
            matches.append(match)
        
        # Sort by overall score (descending)
        matches.sort(key=lambda x: x.match_score.overall_score, reverse=True)
        
        return matches

# Global instance
matching_engine = AIMatchingEngine()

def calculate_job_candidate_match(candidate: Candidate, job: JobPosting, parsed_job: ParsedJobData = None) -> JobMatch:
    """
    Calculate match between a candidate and job
    """
    return matching_engine.calculate_job_match(candidate, job, parsed_job)

def rank_jobs_for_candidate(candidate: Candidate, jobs: List[JobPosting], parsed_jobs: List[ParsedJobData] = None) -> List[JobMatch]:
    """
    Rank jobs for a candidate
    """
    return matching_engine.rank_jobs_for_candidate(candidate, jobs, parsed_jobs)

def find_best_candidates_for_job(job: JobPosting, candidates: List[Candidate], parsed_job: ParsedJobData = None) -> List[JobMatch]:
    """
    Find best candidates for a job
    """
    return matching_engine.find_best_candidates_for_job(job, candidates, parsed_job)