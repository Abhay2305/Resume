"""Errors domain router.

API endpoints for error log querying and management.
All endpoints require admin authentication.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models.identity import User
from ..schemas.error import (
    ErrorActionResponse,
    ErrorListResponse,
    ErrorOut,
    ErrorStatsResponse,
)
from ..services.error_service import ErrorService

router = APIRouter(prefix="/errors", tags=["Errors"])


def _paginate(items: list, total: int, page: int, size: int) -> dict:
    """Build paginated response dict."""
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "totalPages": max(1, -(-total // size)),
    }


# ---------------------------------------------------------------------------
# GET /api/errors — List errors (paginated, filterable)
# ---------------------------------------------------------------------------

@router.get("", response_model=ErrorListResponse)
def list_errors(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    error_type: Optional[str] = Query(None),
    router: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get paginated error logs with filters.

    Requires admin role.
    """
    service = ErrorService(db)
    end = end_date or datetime.utcnow()
    start = start_date or (end - timedelta(days=30))

    errors = service.get_error_history(
        error_type=error_type,
        severity=severity,
        status=status,
        start=start,
        end=end,
        limit=1000,
    )

    # Apply text search filter
    if search:
        errors = [
            e for e in errors
            if search.lower() in (e.error_message or "").lower()
            or search.lower() in (e.error_type or "").lower()
            or search.lower() in (e.endpoint or "").lower()
        ]

    # Apply router filter
    if router:
        errors = [e for e in errors if (e.router or "").lower() == router.lower()]

    total = len(errors)
    start_idx = (page - 1) * size
    page_items = errors[start_idx : start_idx + size]

    return ErrorListResponse(
        **_paginate(
            [ErrorOut.model_validate(e) for e in page_items],
            total,
            page,
            size,
        )
    )


# ---------------------------------------------------------------------------
# GET /api/errors/stats — Error statistics
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=ErrorStatsResponse)
def get_error_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get error statistics (counts by severity, status, type, resolution rate).

    Requires admin role.
    """
    service = ErrorService(db)
    end = end_date or datetime.utcnow()
    start = start_date or (end - timedelta(days=30))

    stats = service.get_error_statistics(start=start, end=end)
    resolution_rate = service._calculate_resolution_rate(start, end)

    return ErrorStatsResponse(
        total=stats["total_count"],
        by_severity=stats["by_severity"],
        by_status=stats["by_status"],
        top_types=stats["top_types"],
        resolution_rate=resolution_rate,
    )


# ---------------------------------------------------------------------------
# GET /api/errors/{error_id} — Error detail
# ---------------------------------------------------------------------------

@router.get("/{error_id}", response_model=ErrorOut)
def get_error(
    error_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get a single error by ID.

    Requires admin role.
    """
    service = ErrorService(db)
    error = service.get_error(error_id)
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    return ErrorOut.model_validate(error)


# ---------------------------------------------------------------------------
# POST /api/errors/{error_id}/acknowledge — Acknowledge error
# ---------------------------------------------------------------------------

@router.post("/{error_id}/acknowledge", response_model=ErrorActionResponse)
def acknowledge_error(
    error_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Acknowledge an error.

    Requires admin role.
    """
    service = ErrorService(db)
    error = service.acknowledge_error(error_id)
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    return ErrorActionResponse(
        success=True,
        error=ErrorOut.model_validate(error),
        message="Error acknowledged",
    )


# ---------------------------------------------------------------------------
# POST /api/errors/{error_id}/resolve — Resolve error
# ---------------------------------------------------------------------------

@router.post("/{error_id}/resolve", response_model=ErrorActionResponse)
def resolve_error(
    error_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Resolve an error.

    Requires admin role.
    """
    service = ErrorService(db)
    error = service.logs.update_status(error_id, "resolved")
    if not error:
        raise HTTPException(status_code=404, detail="Error not found")
    return ErrorActionResponse(
        success=True,
        error=ErrorOut.model_validate(error),
        message="Error resolved",
    )
