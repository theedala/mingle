"""
Analytics routes - insights and data for ML pipeline.
"""
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.clickhouse import get_matching_insights, get_popular_interests
from app.models.schemas import MatchInsights, PopularInterest

router = APIRouter()


@router.get("/insights", response_model=MatchInsights)
async def get_insights(days: int = 30):
    """
    Get matching algorithm performance insights.
    
    Returns aggregated metrics for the last N days.
    """
    insights = get_matching_insights(days)
    
    return MatchInsights(
        avg_compatibility=insights.get("avg_compatibility", 0),
        avg_duration_seconds=insights.get("avg_duration_seconds", 0),
        avg_messages=insights.get("avg_messages", 0),
        completion_rate=insights.get("completion_rate", 0),
        avg_quality_rating=insights.get("avg_quality_rating"),
    )


@router.get("/interests/popular", response_model=List[PopularInterest])
async def get_popular(limit: int = 20):
    """
    Get the most popular interests.
    
    Useful for suggesting interests to new users.
    """
    interests = get_popular_interests(limit)
    
    return [
        PopularInterest(interest=i["interest"], count=i["count"])
        for i in interests
    ]


@router.get("/interests/trending")
async def get_trending_interests():
    """
    Get trending interests (growing in popularity).
    
    Compares last 7 days vs previous 7 days.
    """
    # Simplified - would compare time periods in production
    popular = get_popular_interests(10)
    
    return {
        "trending": [
            {"interest": i["interest"], "growth": "📈"} 
            for i in popular[:5]
        ]
    }


class HealthMetrics(BaseModel):
    """Platform health metrics."""
    active_users_24h: int
    matches_today: int
    avg_wait_time_seconds: float
    satisfaction_rate: float


@router.get("/health", response_model=HealthMetrics)
async def get_platform_health():
    """
    Get platform health metrics.
    
    Used for monitoring and dashboards.
    """
    # Mock data - would query actual metrics in production
    return HealthMetrics(
        active_users_24h=1250,
        matches_today=340,
        avg_wait_time_seconds=45.5,
        satisfaction_rate=0.82,
    )
