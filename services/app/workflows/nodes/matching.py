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

# Configurable matching threshold (set to 0.4 for production)
MATCHING_THRESHOLD = float(os.getenv("MATCHING_THRESHOLD", "0.4"))

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

        # For sentence transformers, cosine similarity is typically between 0 and 1
        # No normalization needed - use the raw similarity score
        score = max(0.0, min(1.0, similarity))
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
    print("🚨 MATCHING NODE CALLED - DEBUG")
    logger.info("🚨 MATCHING NODE CALLED - DEBUG")
    try:
        print("🔄 Starting AI matching with Sentence Transformers")
        logger.info("🔄 Starting AI matching with Sentence Transformers")
        logger.info(f"🤖 Model: sentence-transformers/all-MiniLM-L6-v2 (FREE)")
        print(f"🤖 Model: sentence-transformers/all-MiniLM-L6-v2 (FREE)")
        logger.info(f"🎯 Using matching threshold: {MATCHING_THRESHOLD}")
        logger.info(f"🔍 State keys available: {list(state.keys())}")

        quality_checked_jobs = state.get("quality_checked_jobs", state.get("parsed_jobs", []))
        print(f"📋 Jobs to match: {len(quality_checked_jobs)}")
        logger.info(f"📋 Jobs to match: {len(quality_checked_jobs)}")

        if not quality_checked_jobs:
            print("⚠️ No jobs to match - skipping matching")
            logger.warning("⚠️ No jobs to match - skipping matching")
            state["matched_jobs"] = []
            return state

        print("✅ Proceeding with matching - jobs found!")
        logger.info("✅ Proceeding with matching - jobs found!")

    except Exception as e:
        print(f"❌ Error in matching node initialization: {e}")
        logger.error(f"❌ Error in matching node initialization: {e}", exc_info=True)
        state["matched_jobs"] = []
        return state

    # Get real candidates from database
    print("🔄 Starting database connection for candidates...")
    logger.info("🔄 Starting database connection for candidates...")
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        from dotenv import load_dotenv

        load_dotenv()
        mongodb_uri = os.getenv("MONGODB_URI")
        print(f"🔗 Connecting to MongoDB...")
        logger.info(f"🔗 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongodb_uri)
        db = client.ai_recruitment
        candidates_collection = db.candidates

        # Fetch all candidates (removed availability filter - was blocking all matches)
        print("🔍 Fetching candidates from database...")
        logger.info("🔍 Fetching candidates from database...")
        candidates_cursor = candidates_collection.find({})
        db_candidates = await candidates_cursor.to_list(length=None)

        print(f"📊 Found {len(db_candidates)} raw candidates in database")
        logger.info(f"📊 Found {len(db_candidates)} raw candidates in database")

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

        print(f"📋 Loaded {len(candidates)} candidates from database")
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

    print(f"🚨 DEBUG: Processing {len(quality_checked_jobs)} quality checked jobs")
    logger.info(f"🚨 DEBUG: Processing {len(quality_checked_jobs)} quality checked jobs")

    for job_idx, job in enumerate(quality_checked_jobs):
        try:
            job_title = job.get('title', 'Unknown Job')
            print(f"🔍 Processing job {job_idx+1}/{len(quality_checked_jobs)}: {job_title} at {job.get('company', 'Unknown Company')}")
            logger.info(f"🔍 Processing job {job_idx+1}/{len(quality_checked_jobs)}: {job_title} at {job.get('company', 'Unknown Company')}")

            # Create job description for embedding
            job_text = f"""
            Job Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Skills Required: {', '.join(job.get('skills_required', []))}
            Experience: {job.get('experience_years_required', 0)} years
            Description: {job.get('description', '')[:500]}
            """

            print(f"🔧 DEBUG: About to get job embedding for: {job_title}")
            logger.info(f"🔧 DEBUG: About to get job embedding for: {job_title}")

            # Get job embedding
            job_embedding = get_embedding(job_text.strip())
            print(f"🔧 DEBUG: Job embedding result: {len(job_embedding) if job_embedding else 'None'}")
            logger.info(f"🔧 DEBUG: Job embedding result: {len(job_embedding) if job_embedding else 'None'}")

            if not job_embedding:
                print(f"❌ Failed to get embedding for job: {job.get('title', 'Unknown')}")
                logger.warning(f"❌ Failed to get embedding for job: {job.get('title', 'Unknown')}")
                continue

            total_api_calls += 1
            matches = []

            # Match against each candidate
            print(f"   🔍 Matching against {len(candidates)} candidates...")
            logger.info(f"   🔍 Matching against {len(candidates)} candidates...")

            for candidate_idx, candidate in enumerate(candidates):
                try:
                    print(f"   🔧 DEBUG: Processing candidate {candidate_idx+1}/{len(candidates)}: {candidate['name']}")
                    logger.info(f"   🔧 DEBUG: Processing candidate {candidate_idx+1}/{len(candidates)}: {candidate['name']}")

                    # Create candidate description for embedding
                    candidate_text = f"""
                    Name: {candidate['name']}
                    Skills: {', '.join(candidate['skills'])}
                    Experience: {candidate['experience']} years
                    Location: {candidate['location']}
                    Summary: {candidate['summary']}
                    """

                    print(f"   🔧 DEBUG: About to get candidate embedding for: {candidate['name']}")
                    logger.info(f"   🔧 DEBUG: About to get candidate embedding for: {candidate['name']}")

                    # Get candidate embedding
                    candidate_embedding = get_embedding(candidate_text.strip())
                    print(f"   🔧 DEBUG: Candidate embedding result: {len(candidate_embedding) if candidate_embedding else 'None'}")
                    logger.info(f"   🔧 DEBUG: Candidate embedding result: {len(candidate_embedding) if candidate_embedding else 'None'}")

                    if not candidate_embedding:
                        print(f"    Failed to get embedding for candidate: {candidate['name']}")
                        logger.warning(f"    Failed to get embedding for candidate: {candidate['name']}")
                        continue

                    total_api_calls += 1

                    # Calculate similarity score
                    similarity_score = calculate_similarity_score(job_embedding, candidate_embedding)

                    # Log similarity score for debugging
                    print(f"    {candidate['name']}: similarity = {similarity_score:.3f} (threshold: {MATCHING_THRESHOLD})")
                    logger.info(f"    {candidate['name']}: similarity = {similarity_score:.3f} (threshold: {MATCHING_THRESHOLD})")

                    # Only include matches above threshold (configurable, default 0.5)
                    if similarity_score >= MATCHING_THRESHOLD:
                        reasons = generate_match_reasoning(job, candidate, similarity_score)

                        print(f"   ✅ MATCH FOUND: {candidate['name']} with score {similarity_score:.3f}")
                        logger.info(f"   ✅ MATCH FOUND: {candidate['name']} with score {similarity_score:.3f}")

                        matches.append({
                            "candidate_id": candidate["id"],
                            "candidate_name": candidate["name"],
                            "candidate_email": candidate["email"],
                            "score": similarity_score,
                            "reasons": reasons,
                            "candidate_skills": candidate["skills"][:3],  # Top 3 skills
                            "candidate_experience": candidate["experience"]
                        })
                    else:
                        print(f"   ❌ Below threshold: {candidate['name']} ({similarity_score:.3f} < {MATCHING_THRESHOLD})")
                        logger.debug(f"   ❌ Below threshold: {candidate['name']} ({similarity_score:.3f} < {MATCHING_THRESHOLD})")

                except Exception as e:
                    logger.error(f"Error matching candidate {candidate['name']}: {e}")
                    continue

            # Sort matches by score (highest first) and take top 3 best candidates
            matches.sort(key=lambda x: x["score"], reverse=True)
            top_matches = matches[:3]  # Always take top 3 highest scoring candidates

            # Log matching results
            print(f"   ✅ Found {len(matches)} total matches, selected top {len(top_matches)}")
            logger.info(f"   ✅ Found {len(matches)} total matches, selected top {len(top_matches)}")
            for i, match in enumerate(top_matches, 1):
                print(f"   {i}. {match['candidate_name']} (Score: {match['score']:.3f})")
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

    print(f"✅ AI Matching completed:")
    print(f"   📊 Jobs processed: {len(matched_jobs)}")
    print(f"   🎯 Total matches found: {total_matches}")
    print(f"   🤖 Sentence Transformer embeddings: {total_api_calls}")
    print(f"   💰 Cost: $0.00 (FREE vs OpenAI ~$0.50-2.00)")
    print(f"   🎚️ Threshold used: {MATCHING_THRESHOLD}")
    if all_scores:
        print(f"   📈 Score range: {min_score:.3f} - {max_score:.3f} (avg: {avg_score:.3f})")

    logger.info(f"✅ AI Matching completed:")
    logger.info(f"   📊 Jobs processed: {len(matched_jobs)}")
    logger.info(f"   🎯 Total matches found: {total_matches}")
    logger.info(f"   🤖 Sentence Transformer embeddings: {total_api_calls}")
    logger.info(f"   💰 Cost: $0.00 (FREE vs OpenAI ~$0.50-2.00)")
    logger.info(f"   🎚️ Threshold used: {MATCHING_THRESHOLD}")
    if all_scores:
        logger.info(f"   📈 Score range: {min_score:.3f} - {max_score:.3f} (avg: {avg_score:.3f})")

    # DEBUG: Show detailed match information
    for i, job in enumerate(matched_jobs):
        job_matches = job.get("matches", [])
        print(f"🔍 DEBUG Job {i+1}: '{job.get('title')}' has {len(job_matches)} matches")
        logger.info(f"🔍 DEBUG Job {i+1}: '{job.get('title')}' has {len(job_matches)} matches")
        for j, match in enumerate(job_matches):
            print(f"   Match {j+1}: {match.get('candidate_name')} (ID: {match.get('candidate_id')}) - Score: {match.get('score', 0):.3f}")
            logger.info(f"   Match {j+1}: {match.get('candidate_name')} (ID: {match.get('candidate_id')}) - Score: {match.get('score', 0):.3f}")

    return state
