"""PROCS Dashboard Router.

API endpoints for PROCS dashboard data.
All routes require admin authentication and are prefixed with /api/procs/dashboard.
"""
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_admin
from ..models.identity import User
from ..services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["PROCS Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get aggregated dashboard statistics.

    Returns counts for users, resumes, cover letters, AI requests,
    errors, subscriptions, opportunities, and ATS results.
    """
    service = DashboardService(db)
    return service.get_stats()


@router.get("/activity")
def get_dashboard_activity(
    limit: int = Query(10, ge=1, le=50),
    cursor: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get recent activity feed from audit logs with cursor pagination."""
    service = DashboardService(db)
    return service.get_activity(limit=limit, cursor=cursor)


@router.get("/health")
def get_dashboard_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get system health status."""
    service = DashboardService(db)
    return service.get_health()


@router.get("/recent")
def get_dashboard_recent(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get recent items (errors and activity)."""
    service = DashboardService(db)
    return service.get_recent(limit=limit)


@router.get("/metrics")
def get_dashboard_metrics(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get metric cards data with trend calculations.

    Returns 6 metrics (Total Users, Active Users, Total Resumes,
    AI Requests, System Errors, Revenue MTD) with trend percentages
    comparing the current period to the previous period.
    """
    service = DashboardService(db)
    return service.get_metrics(period=period)


@router.get("/charts/requests")
def get_chart_requests(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get request volume time-series data for charts."""
    service = DashboardService(db)
    return service.get_request_chart(period=period)


@router.get("/charts/errors")
def get_chart_errors(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get error count time-series data for charts."""
    service = DashboardService(db)
    return service.get_error_chart(period=period)


@router.get("/charts/ai-cost")
def get_chart_ai_cost(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get AI cost time-series data for charts."""
    service = DashboardService(db)
    return service.get_ai_cost_chart(period=period)
