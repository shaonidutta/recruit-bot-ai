"""
Analytics API Routes
Provides real analytics data for dashboard charts and metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, Depends
from bson import ObjectId

from ..models.job import JobService
from ..models.candidate import CandidateService
from ..models.match import MatchService
from ..utils.response_helper import send_success, send_error
from ..auth.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=30),
    current_user = Depends(get_current_user_optional)
):
    """
    Get comprehensive dashboard analytics
    GET /api/v1/analytics/dashboard?days=7
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Check database connection first
        try:
            jobs_collection = JobService.get_collection()
            matches_collection = MatchService.get_collection()
            candidates_collection = CandidateService.get_collection()
        except ConnectionError:
            # Return mock data when database is not available
            return send_success(
                data={
                    "job_trends": [],
                    "source_breakdown": [
                        {"name": "LinkedIn", "value": 40, "color": "#0077B5"},
                        {"name": "Indeed", "value": 35, "color": "#2557A7"},
                        {"name": "Google Jobs", "value": 25, "color": "#4285F4"}
                    ],
                    "workflow_performance": [
                        {"stage": "Scraping", "success_rate": 95, "color": "#10B981"},
                        {"stage": "Parsing", "success_rate": 88, "color": "#3B82F6"},
                        {"stage": "Matching", "success_rate": 75, "color": "#8B5CF6"},
                        {"stage": "Outreach", "success_rate": 60, "color": "#F59E0B"}
                    ],
                    "email_performance": [
                        {"metric": "Sent", "value": 0, "color": "#3B82F6"},
                        {"metric": "Delivered", "value": 0, "color": "#10B981"},
                        {"metric": "Opened", "value": 0, "color": "#F59E0B"},
                        {"metric": "Replied", "value": 0, "color": "#8B5CF6"}
                    ],
                    "summary_stats": {
                        "total_jobs": 0,
                        "total_matches": 0,
                        "total_candidates": 0,
                        "active_workflows": 0,
                        "success_rate": 0,
                        "period_days": days,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                },
                message="Dashboard analytics (database offline - showing demo data)"
            )
        
        # Job discovery trends (daily breakdown)
        job_trends = []
        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Count jobs discovered on this day
            jobs_count = await jobs_collection.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            # Count matches created on this day
            matches_count = await matches_collection.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end},
                "is_active": True
            })
            
            # TODO: Add email count when email tracking is implemented
            emails_count = 0  # Placeholder for now
            
            job_trends.append({
                "date": day_start.strftime("%b %d"),
                "jobs": jobs_count,
                "matches": matches_count,
                "emails": emails_count
            })
        
        # Job source breakdown (using 'via' field where source info is actually stored)
        source_pipeline = [
            {"$group": {
                "_id": "$via",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        source_results = await jobs_collection.aggregate(source_pipeline).to_list(10)
        total_jobs = sum(result["count"] for result in source_results)
        
        source_breakdown = []
        source_colors = {
            "linkedin": "#0077B5",
            "indeed": "#2557A7", 
            "google": "#4285F4",
            "manual": "#6B7280"
        }
        
        for result in source_results:
            source_name = result["_id"] or "Unknown"
            percentage = round((result["count"] / total_jobs * 100) if total_jobs > 0 else 0, 1)
            source_breakdown.append({
                "name": source_name.title(),
                "value": percentage,
                "count": result["count"],
                "color": source_colors.get(source_name.lower(), "#6B7280")
            })
        
        # Workflow success rates (based on actual data)
        total_jobs_processed = await jobs_collection.count_documents({})
        successful_jobs = await jobs_collection.count_documents({"status": {"$ne": "failed"}})
        
        total_matches_attempted = await matches_collection.count_documents({})
        successful_matches = await matches_collection.count_documents({"is_active": True})
        
        # Calculate success rates
        job_success_rate = round((successful_jobs / total_jobs_processed * 100) if total_jobs_processed > 0 else 0, 1)
        match_success_rate = round((successful_matches / total_matches_attempted * 100) if total_matches_attempted > 0 else 0, 1)
        
        workflow_success = [
            {
                "name": "Job Discovery",
                "success": job_success_rate,
                "failed": 100 - job_success_rate,
                "total": total_jobs_processed
            },
            {
                "name": "Candidate Matching", 
                "success": match_success_rate,
                "failed": 100 - match_success_rate,
                "total": total_matches_attempted
            },
            {
                "name": "Email Delivery",
                "success": 0,  # TODO: Implement when email tracking is added
                "failed": 0,
                "total": 0
            },
            {
                "name": "Response Rate",
                "success": 0,  # TODO: Implement when email tracking is added
                "failed": 0,
                "total": 0
            }
        ]
        
        # Email performance (placeholder for now)
        email_performance = [
            {"metric": "Sent", "value": 0, "color": "#3B82F6"},
            {"metric": "Delivered", "value": 0, "color": "#10B981"},
            {"metric": "Opened", "value": 0, "color": "#F59E0B"},
            {"metric": "Replied", "value": 0, "color": "#8B5CF6"}
        ]
        
        # Summary statistics
        summary_stats = {
            "total_jobs": total_jobs_processed,
            "total_matches": successful_matches,
            "total_candidates": await candidates_collection.count_documents({}),
            "active_workflows": 1,  # TODO: Track active workflows
            "success_rate": job_success_rate,
            "period_days": days,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return send_success(
            data={
                "job_trends": job_trends,
                "source_breakdown": source_breakdown,
                "workflow_success": workflow_success,
                "email_performance": email_performance,
                "summary": summary_stats
            },
            message="Dashboard analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard analytics: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve dashboard analytics: {str(e)}", 500)

@router.get("/analytics/trends")
async def get_trend_analytics(
    metric: str = Query("jobs", description="Metric to analyze: jobs, matches, candidates"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=90),
    current_user = Depends(get_current_user_optional)
):
    """
    Get trend analytics for specific metrics
    GET /api/v1/analytics/trends?metric=jobs&days=30
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Select collection based on metric
        try:
            if metric == "jobs":
                collection = JobService.get_collection()
            elif metric == "matches":
                collection = MatchService.get_collection()
            elif metric == "candidates":
                collection = CandidateService.get_collection()
            else:
                return send_error("Invalid metric. Use: jobs, matches, or candidates", 400)
        except ConnectionError:
            # Return empty trends when database is not available
            return send_success(
                data={
                    "trends": [],
                    "metric": metric,
                    "period_days": days,
                    "total_count": 0
                },
                message=f"Trend analytics for {metric} (database offline - no data available)"
            )
        
        # Build aggregation pipeline for daily counts
        pipeline = [
            {
                "$match": {
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
            }
        ]
        
        # Add match-specific filter
        if metric == "matches":
            pipeline[0]["$match"]["is_active"] = True
        
        results = await collection.aggregate(pipeline).to_list(days)
        
        # Format results
        trend_data = []
        for result in results:
            date_obj = datetime(
                result["_id"]["year"],
                result["_id"]["month"], 
                result["_id"]["day"]
            )
            trend_data.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "value": result["count"],
                "formatted_date": date_obj.strftime("%b %d")
            })
        
        return send_success(
            data={
                "metric": metric,
                "period_days": days,
                "trend_data": trend_data,
                "total_records": sum(item["value"] for item in trend_data)
            },
            message=f"{metric.title()} trend analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving trend analytics: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve trend analytics: {str(e)}", 500)

@router.get("/analytics/performance")
async def get_performance_metrics(
    current_user = Depends(get_current_user_optional)
):
    """
    Get performance metrics and KPIs
    GET /api/v1/analytics/performance
    """
    try:
        # Check database connection first
        try:
            jobs_collection = JobService.get_collection()
            matches_collection = MatchService.get_collection()
            candidates_collection = CandidateService.get_collection()
        except ConnectionError:
            # Return mock data when database is not available
            return send_success(
                data={
                    "kpis": {
                        "total_jobs": 0,
                        "total_matches": 0,
                        "total_candidates": 0,
                        "match_rate": 0,
                        "candidate_utilization": 0
                    },
                    "match_quality": {
                        "avg_score": 0,
                        "max_score": 0,
                        "min_score": 0,
                        "total_matches": 0
                    },
                    "efficiency_metrics": {
                        "jobs_per_hour": 0,
                        "matches_per_job": 0,
                        "processing_time": 0
                    }
                },
                message="Performance metrics (database offline - showing demo data)"
            )
        
        # Calculate key performance indicators
        total_jobs = await jobs_collection.count_documents({})
        total_matches = await matches_collection.count_documents({"is_active": True})
        total_candidates = await candidates_collection.count_documents({})
        
        # Match quality metrics
        match_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$match_score"},
                "max_score": {"$max": "$match_score"},
                "min_score": {"$min": "$match_score"},
                "total_matches": {"$sum": 1}
            }}
        ]
        
        match_stats = await matches_collection.aggregate(match_pipeline).to_list(1)
        match_quality = match_stats[0] if match_stats else {
            "avg_score": 0, "max_score": 0, "min_score": 0, "total_matches": 0
        }
        
        # Calculate efficiency metrics
        match_rate = round((total_matches / total_jobs) if total_jobs > 0 else 0, 2)
        candidate_utilization = round((total_matches / total_candidates) if total_candidates > 0 else 0, 2)
        
        performance_data = {
            "overview": {
                "total_jobs": total_jobs,
                "total_matches": total_matches,
                "total_candidates": total_candidates,
                "match_rate": match_rate,
                "candidate_utilization": candidate_utilization
            },
            "match_quality": {
                "average_score": round(match_quality["avg_score"], 3) if match_quality["avg_score"] else 0,
                "highest_score": round(match_quality["max_score"], 3) if match_quality["max_score"] else 0,
                "lowest_score": round(match_quality["min_score"], 3) if match_quality["min_score"] else 0,
                "total_evaluated": match_quality["total_matches"]
            },
            "efficiency": {
                "matches_per_job": match_rate,
                "jobs_per_candidate": round((total_jobs / total_candidates) if total_candidates > 0 else 0, 2),
                "utilization_rate": candidate_utilization
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return send_success(
            data=performance_data,
            message="Performance metrics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving performance metrics: {str(e)}", exc_info=True)
        return send_error(f"Failed to retrieve performance metrics: {str(e)}", 500)
