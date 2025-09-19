"""
Match Routes
API endpoints for job-candidate match management
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from ..models.match import MatchService, MatchInDB, MatchResponse
from ..models.job import JobService
from ..models.candidate import CandidateService
from ..utils.response_helper import send_success, send_error
from ..auth.jwt_handler import verify_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/matches")
async def get_matches(
    limit: int = Query(10, ge=1, le=100, description="Number of matches to return"),
    skip: int = Query(0, ge=0, description="Number of matches to skip"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum match score")
):
    """
    Get job-candidate matches with filtering and pagination
    GET /api/v1/matches?limit=10&skip=0&job_id=xxx&min_score=0.5
    """
    try:
        try:
            # Build filter query
            filter_query = {"is_active": True}
            if job_id:
                filter_query["job_id"] = job_id
            if candidate_id:
                filter_query["candidate_id"] = candidate_id
            if min_score is not None:
                filter_query["match_score"] = {"$gte": min_score}

            # Get matches from database
            collection = MatchService.get_collection()
            cursor = collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        except ConnectionError:
            logger.warning("Database connection not available - returning empty matches")
            return send_success(
                data={
                    "matches": [],
                    "total": 0,
                    "skip": skip,
                    "limit": limit,
                    "has_more": False
                },
                message="Matches retrieved (database offline - no data available)"
            )

        matches = []
        async for match_doc in cursor:
            # Enrich match with job and candidate details
            match_data = await _enrich_match_data(match_doc)
            matches.append(match_data)

        total_count = await collection.count_documents(filter_query)

        return send_success(
            data={
                "matches": matches,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "total": total_count,
                    "has_more": skip + limit < total_count
                },
                "filters": {
                    "job_id": job_id,
                    "candidate_id": candidate_id,
                    "min_score": min_score
                }
            },
            message=f"Retrieved {len(matches)} matches successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving matches: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve matches: {str(e)}", 500)

@router.get("/matches/recent")
async def get_recent_matches(
    limit: int = Query(10, ge=1, le=50, description="Number of recent matches to return"),
    hours: int = Query(24, ge=1, le=168, description="Look back this many hours")
):
    """
    Get recent matches from the last N hours
    GET /api/v1/matches/recent?limit=10&hours=24
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Query recent matches
        collection = MatchService.get_collection()
        cursor = collection.find({
            "is_active": True,
            "created_at": {"$gte": time_threshold}
        }).sort("created_at", -1).limit(limit)

        matches = []
        async for match_doc in cursor:
            # Enrich match with job and candidate details
            match_data = await _enrich_match_data(match_doc, include_full_details=True)
            matches.append(match_data)

        return send_success(
            data={
                "matches": matches,
                "count": len(matches),
                "time_range": {
                    "hours": hours,
                    "since": time_threshold.isoformat(),
                    "until": datetime.utcnow().isoformat()
                }
            },
            message=f"Retrieved {len(matches)} recent matches from last {hours} hours"
        )
    except Exception as e:
        logger.error(f"Error retrieving recent matches: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve recent matches: {str(e)}", 500)

@router.get("/matches/stats")
async def get_match_statistics():
    """
    Get match statistics and metrics
    GET /api/v1/matches/stats
    """
    try:
        collection = MatchService.get_collection()

        # Total matches
        total_matches = await collection.count_documents({"is_active": True})

        # Recent matches (last 24 hours)
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        recent_matches = await collection.count_documents({
            "is_active": True,
            "created_at": {"$gte": time_threshold}
        })

        # Average match score
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$match_score"},
                "max_score": {"$max": "$match_score"},
                "min_score": {"$min": "$match_score"}
            }}
        ]

        score_stats = await collection.aggregate(pipeline).to_list(1)
        avg_score = score_stats[0]["avg_score"] if score_stats else 0.0
        max_score = score_stats[0]["max_score"] if score_stats else 0.0
        min_score = score_stats[0]["min_score"] if score_stats else 0.0

        # Score distribution
        score_ranges = [
            {"range": "0.9-1.0", "min": 0.9, "max": 1.0},
            {"range": "0.8-0.9", "min": 0.8, "max": 0.9},
            {"range": "0.7-0.8", "min": 0.7, "max": 0.8},
            {"range": "0.6-0.7", "min": 0.6, "max": 0.7},
            {"range": "0.5-0.6", "min": 0.5, "max": 0.6},
            {"range": "0.0-0.5", "min": 0.0, "max": 0.5}
        ]

        distribution = []
        for range_info in score_ranges:
            count = await collection.count_documents({
                "is_active": True,
                "match_score": {"$gte": range_info["min"], "$lt": range_info["max"]}
            })
            distribution.append({
                "range": range_info["range"],
                "count": count,
                "percentage": round((count / total_matches * 100) if total_matches > 0 else 0, 1)
            })

        return send_success(
            data={
                "total_matches": total_matches,
                "recent_matches_24h": recent_matches,
                "score_statistics": {
                    "average": round(avg_score, 3),
                    "maximum": round(max_score, 3),
                    "minimum": round(min_score, 3)
                },
                "score_distribution": distribution,
                "generated_at": datetime.utcnow().isoformat()
            },
            message="Match statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving match statistics: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve match statistics: {str(e)}", 500)

@router.get("/matches/{match_id}")
async def get_match_by_id(
    match_id: str = Path(..., description="Match ID")
):
    """
    Get specific match by ID with full details
    GET /api/v1/matches/{match_id}
    """
    try:
        collection = MatchService.get_collection()
        # Convert string ID to ObjectId
        try:
            object_id = ObjectId(match_id)
        except Exception:
            return send_error("Invalid match ID format", 400)

        match_doc = await collection.find_one({"_id": object_id, "is_active": True})

        if not match_doc:
            return send_error("Match not found", 404)

        # Enrich match with full job and candidate details
        match_data = await _enrich_match_data(match_doc, include_full_details=True)

        return send_success(
            data=match_data,
            message="Match retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving match {match_id}: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve match: {str(e)}", 500)

@router.get("/jobs/{job_id}/matches")
async def get_matches_for_job(
    job_id: str = Path(..., description="Job ID"),
    limit: int = Query(20, ge=1, le=100),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0)
):
    """
    Get all matches for a specific job
    GET /api/v1/jobs/{job_id}/matches?limit=20&min_score=0.5
    """
    try:
        # Verify job exists
        job = await JobService.find_by_id(job_id)
        if not job:
            return send_error("Job not found", 404)

        # Build filter query
        filter_query = {"job_id": job_id, "is_active": True}
        if min_score is not None:
            filter_query["match_score"] = {"$gte": min_score}

        # Get matches for this job
        collection = MatchService.get_collection()
        cursor = collection.find(filter_query).sort("match_score", -1).limit(limit)

        matches = []
        async for match_doc in cursor:
            match_data = await _enrich_match_data(match_doc)
            matches.append(match_data)

        return send_success(
            data={
                "job_id": job_id,
                "job_title": job.title,
                "company_name": job.company,
                "matches": matches,
                "count": len(matches),
                "filters": {
                    "min_score": min_score,
                    "limit": limit
                }
            },
            message=f"Retrieved {len(matches)} matches for job"
        )
    except Exception as e:
        logger.error(f"Error retrieving matches for job {job_id}: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve job matches: {str(e)}", 500)

@router.get("/candidates/{candidate_id}/matches")
async def get_matches_for_candidate(
    candidate_id: str = Path(..., description="Candidate ID"),
    limit: int = Query(20, ge=1, le=100),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0)
):
    """
    Get all matches for a specific candidate
    GET /api/v1/candidates/{candidate_id}/matches?limit=20&min_score=0.5
    """
    try:
        # Verify candidate exists
        candidate = await CandidateService.find_by_id(candidate_id)
        if not candidate:
            return send_error("Candidate not found", 404)

        # Build filter query
        filter_query = {"candidate_id": candidate_id, "is_active": True}
        if min_score is not None:
            filter_query["match_score"] = {"$gte": min_score}

        # Get matches for this candidate
        collection = MatchService.get_collection()
        cursor = collection.find(filter_query).sort("match_score", -1).limit(limit)

        matches = []
        async for match_doc in cursor:
            match_data = await _enrich_match_data(match_doc)
            matches.append(match_data)

        return send_success(
            data={
                "candidate_id": candidate_id,
                "candidate_name": f"{candidate.first_name} {candidate.last_name}".strip(),
                "candidate_email": candidate.email,
                "matches": matches,
                "count": len(matches),
                "filters": {
                    "min_score": min_score,
                    "limit": limit
                }
            },
            message=f"Retrieved {len(matches)} matches for candidate"
        )
    except Exception as e:
        logger.error(f"Error retrieving matches for candidate {candidate_id}: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve candidate matches: {str(e)}", 500)

async def _enrich_match_data(match_doc: Dict[str, Any], include_full_details: bool = False) -> Dict[str, Any]:
    """
    Enrich match document with job and candidate details
    """
    try:
        match_data = {
            "id": str(match_doc["_id"]),
            "job_id": match_doc.get("job_id"),
            "candidate_id": match_doc.get("candidate_id"),
            "match_score": match_doc.get("match_score", 0.0),
            "match_reasons": match_doc.get("match_reasons", []),
            "created_at": match_doc.get("created_at").isoformat() if match_doc.get("created_at") else None,
            "updated_at": match_doc.get("updated_at").isoformat() if match_doc.get("updated_at") else None
        }

        # Add job details
        if match_doc.get("job_id"):
            try:
                job = await JobService.find_by_id(match_doc["job_id"])
                if job:
                    match_data["job_title"] = job.title
                    match_data["company_name"] = job.company
                    match_data["job_location"] = job.location
                    if include_full_details:
                        match_data["job_description"] = job.description
                        match_data["job_skills_required"] = job.skills_required
            except Exception as e:
                logger.warning(f"Could not fetch job details for {match_doc['job_id']}: {e}")

        # Add candidate details
        if match_doc.get("candidate_id"):
            try:
                logger.info(f"🔍 DEBUG: Looking up candidate {match_doc['candidate_id']}")

                # DEBUG: Check total candidates in database
                collection = CandidateService.get_collection()
                total_candidates = await collection.count_documents({})
                logger.info(f"📊 DEBUG: Total candidates in database: {total_candidates}")

                candidate = await CandidateService.find_by_id(match_doc["candidate_id"])
                if candidate:
                    logger.info(f"✅ DEBUG: Found candidate {candidate.first_name} {candidate.last_name}")
                    match_data["candidate_name"] = f"{candidate.first_name} {candidate.last_name}".strip()
                    match_data["candidate_email"] = candidate.email
                    match_data["candidate_location"] = candidate.location
                    if include_full_details:
                        match_data["candidate_skills"] = candidate.skills
                        match_data["candidate_experience_years"] = candidate.experience_years
                        match_data["candidate_current_role"] = candidate.current_role
                else:
                    logger.warning(f"❌ DEBUG: No candidate found for ID {match_doc['candidate_id']}")
                    # DEBUG: Show first few candidate IDs in database
                    sample_candidates = await collection.find({}, {"_id": 1, "first_name": 1, "last_name": 1}).limit(3).to_list(3)
                    logger.info(f"📋 DEBUG: Sample candidates: {[(str(c['_id']), c.get('first_name', 'N/A'), c.get('last_name', 'N/A')) for c in sample_candidates]}")
            except Exception as e:
                logger.warning(f"Could not fetch candidate details for {match_doc['candidate_id']}: {e}")

        return match_data
    except Exception as e:
        logger.error(f"Error enriching match data: {e}")
        return match_data
