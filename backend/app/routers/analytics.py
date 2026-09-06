"""PROCS Analytics Router.

API endpoints for analytics data.
All routes require admin authentication and are prefixed with /api/analytics.
"""
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_admin
from ..models.identity import User
from ..schemas.analytics import RevenueResponse, FeatureUsageResponse, FunnelsResponse
from ..repositories.dashboard import DashboardRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["PROCS Analytics"])


@router.get("/revenue")
def get_revenue(
    period: str = Query("30d"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get revenue analytics.

    Requires admin role.
    """
    repo = DashboardRepository(db)
    result = repo.get_revenue_analytics(period=period)

    return RevenueResponse(
        summary=result["summary"],
        series=result["series"],
        period=result["period"],
    )


@router.get("/features")
def get_features(
    period: str = Query("30d"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get feature usage analytics.

    Requires admin role.
    """
    repo = DashboardRepository(db)
    result = repo.get_feature_usage_analytics(period=period)

    return FeatureUsageResponse(
        items=result["items"],
        total=result["total"],
        period=result["period"],
    )


@router.get("/funnels")
def get_funnels(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get funnel conversion analytics.

    Requires admin role.
    """
    repo = DashboardRepository(db)
    result = repo.get_funnel_analytics()

    return FunnelsResponse(funnels=result["funnels"])
