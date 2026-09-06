"""Audit System Router.

API endpoints for querying audit logs. Provides read-only access to audit
trail data for compliance, security monitoring, and debugging.

All routes require admin authentication.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_admin
from ..models.identity import User
from ..schemas.audit import (
    AuditLogListResponse,
    AuditLogOut,
    AuditSummaryResponse,
    AuditActionSummary,
    AuditEntitySummary,
    AuditExportRequest,
    AuditExportResponse,
)
from ..services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit System"])


# ---------------------------------------------------------------------------
# GET /api/audit — List audit logs (paginated, filterable)
# ---------------------------------------------------------------------------

@router.get("", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get paginated audit logs with filters.

    Requires admin role.
    """
    service = AuditService(db)
    result = service.search_logs(
        page=page,
        limit=limit,
        entity_type=entity_type,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )

    return AuditLogListResponse(
        items=[AuditLogOut.model_validate(log) for log in result["items"]],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        totalPages=result["totalPages"],
    )


# ---------------------------------------------------------------------------
# GET /api/audit/summary — Audit summary statistics
# ---------------------------------------------------------------------------

@router.get("/summary", response_model=AuditSummaryResponse)
def get_audit_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get audit summary with action and entity counts.

    Requires admin role.
    """
    service = AuditService(db)
    summary = service.get_summary(start=start_date, end=end_date)

    return AuditSummaryResponse(
        action_summary=[AuditActionSummary(**item) for item in summary["action_summary"]],
        entity_summary=[AuditEntitySummary(**item) for item in summary["entity_summary"]],
        total_errors=summary["total_errors"],
    )


# ---------------------------------------------------------------------------
# GET /api/audit/{entityType}/{entityId} — Entity audit history
# ---------------------------------------------------------------------------

@router.get("/{entity_type}/{entity_id}", response_model=AuditLogListResponse)
def get_entity_audit_history(
    entity_type: str,
    entity_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get audit history for a specific entity.

    Requires admin role.
    """
    service = AuditService(db)
    logs = service.get_entity_history(entity_type, entity_id, limit)

    return AuditLogListResponse(
        items=[AuditLogOut.model_validate(log) for log in logs],
        total=len(logs),
    )


# ---------------------------------------------------------------------------
# GET /api/audit/user/{userId} — User audit history
# ---------------------------------------------------------------------------

@router.get("/user/{user_id}", response_model=AuditLogListResponse)
def get_user_audit_history(
    user_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get audit history for a specific user.

    Requires admin role.
    """
    service = AuditService(db)
    logs = service.get_user_history(user_id, limit=limit, offset=offset, action=action)

    return AuditLogListResponse(
        items=[AuditLogOut.model_validate(log) for log in logs],
        total=len(logs),
    )


# ---------------------------------------------------------------------------
# POST /api/audit/export — Export audit logs (stub)
# ---------------------------------------------------------------------------

@router.post("/export", response_model=AuditExportResponse)
def export_audit_logs(
    request: AuditExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Export audit logs (stub — full implementation in future spec).

    Requires admin role.
    """
    import uuid

    export_id = str(uuid.uuid4())
    logger.info(
        "Audit export requested by user=%s entity_type=%s",
        current_user.id,
        request.entity_type,
    )

    return AuditExportResponse(
        export_id=export_id,
        status="pending",
        message="Export job created (full implementation pending)",
    )
