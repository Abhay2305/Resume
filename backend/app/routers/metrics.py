"""Metrics domain router.

API endpoints for metrics data retrieval, manual flush, and cleanup.
All endpoints require admin authentication.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models.identity import User
from ..schemas.metric import (
    CleanupResponse,
    FlushResponse,
    MetricListResponse,
    MetricOut,
    MetricSummary,
    VALID_METRIC_NAMES,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


def _get_metrics_service(request: Request):
    """Resolve the MetricsService singleton from app.state."""
    service = getattr(request.app.state, "metrics_service", None)
    if service is None:
        raise HTTPException(
            status_code=503,
            detail="Metrics service not available",
        )
    return service


@router.get("", response_model=MetricListResponse)
def list_metrics(
    request: Request,
    metric_name: str = Query(..., description="Metric name (must be in allowlist)"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List metrics by name and time range. Requires admin role."""
    if metric_name not in VALID_METRIC_NAMES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid metric name format: {metric_name}",
        )

    service = _get_metrics_service(request)

    # Default time range: last 24 hours
    now = datetime.utcnow()
    if start_time is None:
        start_time = now - timedelta(hours=24)
    if end_time is None:
        end_time = now

    items, total = service.get_metrics(metric_name, start_time, end_time, page, limit)
    return MetricListResponse(
        items=[MetricOut.model_validate(m) for m in items],
        total=total,
        page=page,
        size=limit,
    )


@router.get("/summary", response_model=MetricSummary)
def get_metrics_summary(
    request: Request,
    start_time: datetime = Query(..., description="Start of time range"),
    end_time: datetime = Query(..., description="End of time range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get aggregated metrics summary for a time period. Requires admin role."""
    service = _get_metrics_service(request)
    return service.get_metrics_summary(start_time, end_time)


@router.post("/flush", response_model=FlushResponse)
def flush_metrics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Manually trigger metrics flush from in-memory buffers to database. Requires admin role."""
    service = _get_metrics_service(request)
    flushed = service.flush()
    return FlushResponse(flushed=flushed)


@router.delete("/cleanup", response_model=CleanupResponse)
def cleanup_metrics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Manually trigger retention cleanup (delete metrics older than 90 days). Requires admin role."""
    service = _get_metrics_service(request)
    deleted = service.cleanup_retention()
    return CleanupResponse(deleted=deleted)
