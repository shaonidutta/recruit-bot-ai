"""
AI-Powered Matching Node using Sentence Transformers
Optimized with parallel processing and caching for improved performance
"""

import logging
import os
import asyncio
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from ...utils.parallel_processing import parallel_processor, performance_monitor
from ...utils.caching import cache_manager, cached_embedding
from ...config.database import get_database

logger = logging.getLogger(__name__)

# Global variable for lazy loading
embedding_model = None

def get_embedding_model():
    """Lazy load Sentence Transformer model to avoid blocking imports"""
    global embedding_model
    if embedding_model is None:
        try:
            logger.info("🔄 Loading Sentence Transformer model: all-MiniLM-L6-v2")
            embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("✅ Loaded Sentence Transformer model successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Sentence Transformer model: {e}")
            embedding_model = None
    return embedding_model

# Configurable matching threshold (set to 0.4 for production)
MATCHING_THRESHOLD = float(os.getenv("MATCHING_THRESHOLD", "0.4"))

@cached_embedding(model_name="all-MiniLM-L6-v2", ttl=604800)  # Cache for 7 days
async def get_cached_embedding(text: str) -> List[float]:
    """Get cached Sentence Transformer embedding for text"""
    try:
        model = get_embedding_model()
        if model is None:
            logger.error("Sentence Transformer model not available")
            return []

        # Get embedding using Sentence Transformers (returns numpy array)
        embedding = model.encode(text, convert_to_tensor=False)
        # Convert numpy array to list of floats
        return [float(x) for x in embedding]
    except Exception as e:
        logger.error(f"Error getting Sentence Transformer embedding: {e}")
        return []

def get_embedding(text: str) -> List[float]:
    """Get Sentence Transformer embedding for text (free alternative to OpenAI)"""
    # For backward compatibility, run async function in sync context
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_cached_embedding(text))
    except RuntimeError:
        # If no event loop, create one
        return asyncio.run(get_cached_embedding(text))

def calculate_similarity_score(job_embedding: List[float], candidate_embedding: List[float]) -> float:
    """Calculate cosine similarity between job and candidate embeddings"""
    if not job_embedding or not candidate_embedding:
        return 0.0

    try:
        # Convert to numpy arrays and reshape for sklearn
        job_vec = np.array(job_embedding).reshape(1, -1)
        candidate_vec = np.array(candidate_embedding).reshape(1, -1)

        # Calculate cosine similarity (returns value between -1 and 1)
        similarity = cosine_similarity(job_vec, candidate_vec)[0][0]

        # For sentence transformers, cosine similarity is typically between 0 and 1
        # No normalization needed - use the raw similarity score
        score = max(0.0, min(1.0, similarity))
        return round(score, 3)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0

def calculate_skill_match_boost(job: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate skill match boost to improve scores for exact skill matches"""
    try:
        # Extract skills from job description and candidate
        job_title = job.get("title", "").lower()
        job_description = job.get("description", "").lower()
        candidate_skills = [skill.lower() for skill in candidate.get("skills", [])]

        if not candidate_skills:
            return 0.0

        # Define key technical skills and their importance
        skill_weights = {
            # Programming languages
            "python": 0.15, "java": 0.15, "javascript": 0.15, "c#": 0.15, ".net": 0.15,
            "react": 0.12, "angular": 0.12, "vue": 0.12, "node.js": 0.12,
            # Databases
            "sql": 0.10, "mysql": 0.10, "postgresql": 0.10, "mongodb": 0.10,
            # Cloud & DevOps
            "aws": 0.10, "azure": 0.10, "docker": 0.08, "kubernetes": 0.08,
            # Data Science
            "machine learning": 0.15, "tensorflow": 0.12, "pandas": 0.10,
            # Other important skills
            "spring": 0.08, "django": 0.08, "flask": 0.08, "express": 0.08
        }

        boost = 0.0
        matched_skills = 0

        # Check for exact skill matches
        for skill in candidate_skills:
            skill_clean = skill.strip().lower()

            # Check if skill appears in job title or description
            if skill_clean in job_title or skill_clean in job_description:
                weight = skill_weights.get(skill_clean, 0.05)  # Default weight for other skills
                boost += weight
                matched_skills += 1

        # Additional boost for multiple skill matches
        if matched_skills >= 3:
            boost += 0.1  # Extra boost for multiple matches
        elif matched_skills >= 2:
            boost += 0.05

        # Cap the boost to prevent over-inflation
        return min(0.4, boost)

    except Exception as e:
        logger.error(f"Error calculating skill boost: {e}")
        return 0.0

def generate_match_reasoning(job: Dict[str, Any], candidate: Dict[str, Any], score: float) -> List[str]:
    """Generate AI-powered match reasoning"""
    reasons = []

    # Skills matching
    job_skills = job.get("skills_required", [])
    candidate_skills = candidate.get("skills", [])

    if job_skills and candidate_skills:
        matching_skills = set(job_skills) & set(candidate_skills)
        if matching_skills:
            reasons.append(f"Skills match: {', '.join(list(matching_skills)[:3])}")

    # Experience matching
    job_exp = job.get("experience_years_required", 0)
    candidate_exp = candidate.get("experience", 0)

    if job_exp and candidate_exp:
        if abs(job_exp - candidate_exp) <= 1:
            reasons.append("Perfect experience level match")
        elif candidate_exp >= job_exp:
            reasons.append("Exceeds required experience")
        else:
            reasons.append("Close experience level match")

    # Score-based reasoning
    if score >= 0.8:
        reasons.append("Excellent overall fit")
    elif score >= 0.7:
        reasons.append("Strong candidate match")
    elif score >= 0.6:
        reasons.append("Good potential match")
    elif score >= 0.5:
        reasons.append("Reasonable match")

    return reasons[:3]  # Limit to top 3 reasons

async def generate_job_embeddings_batch(jobs: List[Dict[str, Any]]) -> List[List[float]]:
    """Generate embeddings for multiple jobs in parallel"""
    async def get_job_embedding(job: Dict[str, Any]) -> List[float]:
        job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('skills', []))}"
        return await get_cached_embedding(job_text)

    # Process jobs in parallel
    embeddings = await asyncio.gather(*[get_job_embedding(job) for job in jobs])
    return embeddings

async def generate_candidate_embeddings_batch(candidates: List[Dict[str, Any]]) -> List[List[float]]:
    """Generate embeddings for multiple candidates in parallel"""
    async def get_candidate_embedding(candidate: Dict[str, Any]) -> List[float]:
        candidate_text = f"{candidate.get('name', '')} {' '.join(candidate.get('skills', []))}"
        return await get_cached_embedding(candidate_text)

    # Process candidates in parallel
    embeddings = await asyncio.gather(*[get_candidate_embedding(candidate) for candidate in candidates])
    return embeddings

@performance_monitor("Enhanced Matching (Parallel + Cached)")
async def matching_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered candidate matching using Sentence Transformers with parallel processing and caching"""
    try:
        logger.info("Starting enhanced AI matching with parallel processing and caching")
        logger.info(f"Using matching threshold: {MATCHING_THRESHOLD}")

        quality_checked_jobs = state.get("quality_checked_jobs", state.get("parsed_jobs", []))
        logger.info(f"Jobs to match: {len(quality_checked_jobs)}")

        # DEBUG: Print state keys to see what's available
        print(f"🔍 DEBUG MATCHING: Available state keys: {list(state.keys())}")
        print(f"🔍 DEBUG MATCHING: Quality checked jobs: {len(quality_checked_jobs)}")
        logger.info(f"🔍 DEBUG Available state keys: {list(state.keys())}")
        if quality_checked_jobs:
            print(f"🔍 DEBUG MATCHING: First job to match: {quality_checked_jobs[0].get('title')} at {quality_checked_jobs[0].get('company')}")
            logger.info(f"🔍 DEBUG First job to match: {quality_checked_jobs[0].get('title')} at {quality_checked_jobs[0].get('company')}")

        if not quality_checked_jobs:
            logger.warning("No jobs to match - skipping matching")
            state["matched_jobs"] = []
            return state

    except Exception as e:
        logger.error(f"Error in matching node initialization: {e}", exc_info=True)
        state["matched_jobs"] = []
        return state

    # Get real candidates from database
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        from dotenv import load_dotenv

        load_dotenv()
        mongodb_uri = os.getenv("MONGODB_URI")
        client = AsyncIOMotorClient(mongodb_uri)
        db = client.ai_recruitment
        candidates_collection = db.candidates

        # Fetch all candidates (removed availability filter - was blocking all matches)
        candidates_cursor = candidates_collection.find({})
        db_candidates = await candidates_cursor.to_list(length=None)

        logger.info(f"Found {len(db_candidates)} candidates in database")

        # Convert to matching format
        candidates = []
        for candidate in db_candidates:
            # Handle both name formats: single "name" field or "first_name" + "last_name"
            if "name" in candidate:
                full_name = candidate["name"]
            else:
                first_name = candidate.get("first_name", "")
                last_name = candidate.get("last_name", "")
                full_name = f"{first_name} {last_name}".strip() or "Unknown"

            candidates.append({
                "id": str(candidate["_id"]),
                "name": full_name,
                "email": candidate.get("email", ""),
                "skills": candidate.get("skills", []),
                "experience": candidate.get("experience_years", 0),  # Fixed: was "experience_years"
                "location": candidate.get("location", ""),
                "summary": candidate.get("summary", "")
            })

        logger.info(f"Loaded {len(candidates)} candidates from database")

        if not candidates:
            logger.warning("No candidates found in database")
            state["matched_jobs"] = []
            return state

    except Exception as e:
        logger.error(f"Failed to load candidates from database: {e}")

    # OPTIMIZATION: Generate all embeddings in parallel batches
    logger.info("🚀 Generating job embeddings in parallel...")
    job_embeddings = await generate_job_embeddings_batch(quality_checked_jobs)

    logger.info("🚀 Generating candidate embeddings in parallel...")
    candidate_embeddings = await generate_candidate_embeddings_batch(candidates)

    matched_jobs = []
    total_comparisons = 0

    logger.info(f"Processing {len(quality_checked_jobs)} jobs against {len(candidates)} candidates")

    # Process all job-candidate combinations with pre-computed embeddings
    for job_idx, (job, job_embedding) in enumerate(zip(quality_checked_jobs, job_embeddings)):
        try:
            job_title = job.get('title', 'Unknown Job')

            if not job_embedding:
                logger.warning(f"Failed to get embedding for job: {job_title}")
                continue

            matches = []

            # Match against each candidate using pre-computed embeddings
            for candidate_idx, (candidate, candidate_embedding) in enumerate(zip(candidates, candidate_embeddings)):
                try:
                    if not candidate_embedding:
                        continue

                    total_comparisons += 1

                    # Calculate similarity score using pre-computed embeddings
                    base_similarity = calculate_similarity_score(job_embedding, candidate_embedding)

                    # Boost score for exact skill matches
                    skill_boost = calculate_skill_match_boost(job, candidate)
                    similarity_score = min(1.0, base_similarity + skill_boost)

                    # Only include matches above threshold (configurable, default 0.5)
                    if similarity_score >= MATCHING_THRESHOLD:
                        reasons = generate_match_reasoning(job, candidate, similarity_score)

                        matches.append({
                            "candidate_id": candidate["id"],
                            "candidate_name": candidate["name"],
                            "candidate_email": candidate["email"],
                            "score": similarity_score,
                            "reasons": reasons,
                            "candidate_skills": candidate["skills"][:3],  # Top 3 skills
                            "candidate_experience": candidate["experience"]
                        })
                except Exception as e:
                    logger.error(f"Error matching candidate {candidate['name']}: {e}")
                    continue

            # Sort matches by score (highest first) and take top 3 best candidates
            matches.sort(key=lambda x: x["score"], reverse=True)
            top_matches = matches[:3]  # Always take top 3 highest scoring candidates

            # Log matching results for this job
            if top_matches:
                logger.info(f"Job '{job_title}': Found {len(top_matches)} matches")
                print(f"🔍 DEBUG MATCHING OUTPUT: Job '{job_title}' has {len(top_matches)} matches")
                print(f"🔍 DEBUG MATCHING OUTPUT: First match: {top_matches[0]}")
            else:
                print(f"🔍 DEBUG MATCHING OUTPUT: Job '{job_title}' has NO matches")

            # Add matched candidates to job for outreach
            job["matches"] = top_matches
            job["match_count"] = len(top_matches)
            job["matched_candidates"] = [
                {
                    "name": match["candidate_name"],
                    "email": match["candidate_email"],
                    "score": match["score"],
                    "skills": match["candidate_skills"]
                }
                for match in top_matches
            ]

            matched_jobs.append(job)

        except Exception as e:
            logger.error(f"Error processing job {job.get('title', 'Unknown')}: {e}")
            continue

    state["matched_jobs"] = matched_jobs
    total_matches = sum(job.get("match_count", 0) for job in matched_jobs)

    # Calculate score statistics for threshold analysis
    all_scores = []
    for job in matched_jobs:
        for match in job.get("matches", []):
            all_scores.append(match.get("score", 0))

    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    max_score = max(all_scores) if all_scores else 0
    min_score = min(all_scores) if all_scores else 0

    logger.info(f"✅ Enhanced AI Matching completed:")
    logger.info(f"   📊 Jobs processed: {len(matched_jobs)}")
    logger.info(f"   🎯 Total matches found: {total_matches}")
    logger.info(f"   🔄 Total comparisons: {total_comparisons}")
    logger.info(f"   🚀 Cached embeddings used: {len(job_embeddings) + len(candidate_embeddings)}")
    logger.info(f"   📏 Threshold used: {MATCHING_THRESHOLD}")
    if all_scores:
        logger.info(f"   📈 Score range: {min_score:.3f} - {max_score:.3f} (avg: {avg_score:.3f})")

    return state
