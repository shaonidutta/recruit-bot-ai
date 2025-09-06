"""
AI-Powered Matching Node using OpenAI Embeddings
"""

import logging
import os
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

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

# Configurable matching threshold (lowered from 0.7 to 0.5 for better matching)
MATCHING_THRESHOLD = float(os.getenv("MATCHING_THRESHOLD", "0.5"))

def get_embedding(text: str) -> List[float]:
    """Get Sentence Transformer embedding for text (free alternative to OpenAI)"""
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

        # Sentence Transformers typically return similarities between 0 and 1 already
        # But we'll normalize to be safe: convert from [-1,1] to [0,1]
        score = max(0.0, min(1.0, (similarity + 1) / 2))
        return round(score, 3)
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
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

async def matching_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """AI-powered candidate matching using Sentence Transformers (free alternative to OpenAI)"""
    logger.info("🔄 Starting AI matching with Sentence Transformers")
    logger.info(f"🤖 Model: sentence-transformers/all-MiniLM-L6-v2 (FREE)")
    logger.info(f"🎯 Using matching threshold: {MATCHING_THRESHOLD}")

    quality_checked_jobs = state.get("quality_checked_jobs", state.get("parsed_jobs", []))
    if not quality_checked_jobs:
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

        # Convert to matching format
        candidates = []
        for candidate in db_candidates:
            candidates.append({
                "id": str(candidate["_id"]),
                "name": candidate.get("name", "Unknown"),
                "email": candidate.get("email", ""),
                "skills": candidate.get("skills", []),
                "experience": candidate.get("experience_years", 0),  # Fixed: was "experience_years"
                "location": candidate.get("location", ""),
                "summary": candidate.get("summary", "")
            })

        logger.info(f"📋 Loaded {len(candidates)} candidates from database")

        # Log candidate sample for debugging
        if candidates:
            sample_candidate = candidates[0]
            logger.info(f"📝 Sample candidate: {sample_candidate['name']} - Skills: {sample_candidate['skills'][:3]} - Exp: {sample_candidate['experience']}y")

        if not candidates:
            logger.warning("⚠️ No candidates found in database")
            state["matched_jobs"] = []
            return state

    except Exception as e:
        logger.error(f"❌ Failed to load candidates from database: {e}")

    matched_jobs = []
    total_api_calls = 0

    for job in quality_checked_jobs:
        try:
            job_title = job.get('title', 'Unknown Job')
            logger.info(f"🔍 Processing job: {job_title} at {job.get('company', 'Unknown Company')}")

            # Create job description for embedding
            job_text = f"""
            Job Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Skills Required: {', '.join(job.get('skills_required', []))}
            Experience: {job.get('experience_years_required', 0)} years
            Description: {job.get('description', '')[:500]}
            """

            # Get job embedding
            job_embedding = get_embedding(job_text.strip())
            if not job_embedding:
                logger.warning(f"Failed to get embedding for job: {job.get('title', 'Unknown')}")
                continue

            total_api_calls += 1
            matches = []

            # Match against each candidate
            for candidate in candidates:
                try:
                    # Create candidate description for embedding
                    candidate_text = f"""
                    Name: {candidate['name']}
                    Skills: {', '.join(candidate['skills'])}
                    Experience: {candidate['experience']} years
                    Location: {candidate['location']}
                    Summary: {candidate['summary']}
                    """

                    # Get candidate embedding
                    candidate_embedding = get_embedding(candidate_text.strip())
                    if not candidate_embedding:
                        continue

                    total_api_calls += 1

                    # Calculate similarity score
                    similarity_score = calculate_similarity_score(job_embedding, candidate_embedding)

                    # Log similarity score for debugging
                    logger.debug(f"   📊 {candidate['name']}: similarity = {similarity_score:.3f}")

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

            # Sort matches by score (highest first) and take top 3
            matches.sort(key=lambda x: x["score"], reverse=True)
            top_matches = matches[:3]

            # Log matching results
            logger.info(f"   ✅ Found {len(matches)} total matches, selected top {len(top_matches)}")
            for i, match in enumerate(top_matches, 1):
                logger.info(f"   {i}. {match['candidate_name']} (Score: {match['score']:.3f})")

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

    logger.info(f"✅ AI Matching completed:")
    logger.info(f"   📊 Jobs processed: {len(matched_jobs)}")
    logger.info(f"   🎯 Total matches found: {total_matches}")
    logger.info(f"   🤖 Sentence Transformer embeddings: {total_api_calls}")
    logger.info(f"   💰 Cost: $0.00 (FREE vs OpenAI ~$0.50-2.00)")
    logger.info(f"   🎚️ Threshold used: {MATCHING_THRESHOLD}")
    if all_scores:
        logger.info(f"   📈 Score range: {min_score:.3f} - {max_score:.3f} (avg: {avg_score:.3f})")

    return state
