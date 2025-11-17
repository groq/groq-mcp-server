"""
Analytics API routes
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from models.base import get_db
from models.user import User
from models.analytics import UserAnalytics, PlatformAnalytics
from models.job import Job
from models.client import Client
from utils.auth import get_current_user

router = APIRouter()


@router.get("/user")
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user analytics for the specified number of days
    """
    start_date = datetime.now() - timedelta(days=days)

    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id,
        UserAnalytics.date >= start_date.date()
    ).order_by(UserAnalytics.date.asc()).all()

    # Calculate totals
    total_jobs_viewed = sum(a.jobs_viewed for a in analytics)
    total_jobs_applied = sum(a.jobs_applied for a in analytics)
    total_reports_viewed = sum(a.vetting_reports_viewed for a in analytics)

    # Calculate success rate (if applied to jobs)
    success_rate = (
        (total_jobs_applied / total_jobs_viewed * 100)
        if total_jobs_viewed > 0 else 0
    )

    return {
        "period_days": days,
        "total_jobs_viewed": total_jobs_viewed,
        "total_jobs_applied": total_jobs_applied,
        "total_vetting_reports_viewed": total_reports_viewed,
        "success_rate": round(success_rate, 2),
        "daily_analytics": [
            {
                "date": a.date,
                "jobs_viewed": a.jobs_viewed,
                "jobs_applied": a.jobs_applied,
                "vetting_reports_viewed": a.vetting_reports_viewed,
                "avg_client_trust_score": float(a.avg_client_trust_score) if a.avg_client_trust_score else None
            }
            for a in analytics
        ]
    }


@router.get("/market")
async def get_market_insights(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get market insights and trends
    """
    start_date = datetime.now() - timedelta(days=days)

    # Platform-wide analytics
    platform_analytics = db.query(PlatformAnalytics).filter(
        PlatformAnalytics.date >= start_date.date()
    ).order_by(PlatformAnalytics.date.desc()).all()

    # Current active jobs count
    active_jobs_count = db.query(Job).filter(Job.is_active == True).count()

    # Average rates
    avg_rates = db.query(
        func.avg(Job.hourly_rate).label('avg_hourly'),
        func.avg(Job.fixed_price).label('avg_fixed')
    ).filter(Job.is_active == True).first()

    # Top skills (from most recent analytics)
    top_skills = platform_analytics[0].top_skills if platform_analytics else {}

    # Top categories
    top_categories = platform_analytics[0].top_categories if platform_analytics else {}

    return {
        "period_days": days,
        "active_jobs": active_jobs_count,
        "average_hourly_rate": float(avg_rates.avg_hourly) if avg_rates.avg_hourly else None,
        "average_fixed_price": float(avg_rates.avg_fixed) if avg_rates.avg_fixed else None,
        "top_skills": top_skills,
        "top_categories": top_categories,
        "daily_trends": [
            {
                "date": a.date,
                "total_jobs_scraped": a.total_jobs_scraped,
                "total_active_jobs": a.total_active_jobs,
                "avg_hourly_rate": float(a.avg_hourly_rate) if a.avg_hourly_rate else None,
                "avg_fixed_price": float(a.avg_fixed_price) if a.avg_fixed_price else None
            }
            for a in platform_analytics
        ]
    }


@router.get("/trends")
async def get_trends(
    db: Session = Depends(get_db)
):
    """
    Get trending skills and categories
    """
    # Get most recent platform analytics
    recent_analytics = db.query(PlatformAnalytics).order_by(
        PlatformAnalytics.date.desc()
    ).first()

    if not recent_analytics:
        return {
            "trending_skills": [],
            "trending_categories": []
        }

    return {
        "trending_skills": recent_analytics.top_skills or {},
        "trending_categories": recent_analytics.top_categories or {},
        "last_updated": recent_analytics.date
    }


@router.get("/client-stats")
async def get_client_statistics(
    db: Session = Depends(get_db)
):
    """
    Get client-related statistics
    """
    # Total clients
    total_clients = db.query(Client).count()

    # Verified clients
    verified_clients = db.query(Client).filter(
        Client.verified_payment == True
    ).count()

    # Flagged clients
    flagged_clients = db.query(Client).filter(
        Client.is_flagged == True
    ).count()

    # Average trust score
    avg_trust_score = db.query(func.avg(Client.trust_score)).scalar()

    # Trust score distribution
    trust_score_dist = db.query(
        func.count(Client.id).label('count'),
        ((Client.trust_score / 10) * 10).label('score_range')
    ).group_by('score_range').all()

    return {
        "total_clients": total_clients,
        "verified_clients": verified_clients,
        "flagged_clients": flagged_clients,
        "average_trust_score": float(avg_trust_score) if avg_trust_score else None,
        "trust_score_distribution": {
            f"{int(score_range)}-{int(score_range)+9}": count
            for count, score_range in trust_score_dist
        }
    }
