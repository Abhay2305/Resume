"""PROCS User Management Router.

API endpoints for PROCS user management.
All routes require admin authentication and are prefixed with /api/procs/users.

Follows the dependency chain: Routers → Services → Repositories → Database
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_auth, require_admin
from ..models.identity import User
from ..schemas.procs_user import (
    UserListResponse,
    UserDetailResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserActionResponse,
    UserStatsResponse,
    UserStatsOut,
    UserTimelineResponse,
    UserTimelineEventOut,
)
from ..services.user_management_service import UserManagementService
from ..services.audit_service import AuditService
from ..repositories.audit import AuditLogRepository
from ..utils.timeline_mapper import map_audit_log_to_timeline_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["PROCS Users"])


@router.get("")
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get paginated user list with filters.

    Requires admin role.
    """
    service = UserManagementService(db)
    result = service.get_users(
        page=page,
        limit=limit,
        search=search,
        is_active=is_active,
        is_verified=is_verified,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return UserListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        totalPages=result["totalPages"],
    )


@router.get("/stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user statistics.

    Requires admin role.
    """
    service = UserManagementService(db)
    stats = service.get_user_stats()

    return UserStatsResponse(data=UserStatsOut(**stats))


@router.get("/{user_id}")
def get_user_detail(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user detail by ID.

    Requires admin role.
    """
    service = UserManagementService(db)
    user = service.get_user_detail(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user roles
    roles = service.get_user_roles(user_id)

    return UserDetailResponse(
        data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "avatar_url": user.avatar_url,
            "timezone": user.timezone,
            "language": user.language,
            "last_login_at": user.last_login_at,
            "last_login_ip": user.last_login_ip,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "password_changed_at": user.password_changed_at,
            "email_verified_at": user.email_verified_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "profile": {
                "job_title": user.profile.job_title if user.profile else None,
                "phone": user.profile.phone if user.profile else None,
                "location": user.profile.location if user.profile else None,
                "company": user.profile.company if user.profile else None,
                "industry": user.profile.industry if user.profile else None,
            } if user.profile else None,
            "roles": roles,
        }
    )


@router.put("/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update user details.

    Requires admin role.
    """
    service = UserManagementService(db)

    # Filter out None values
    update_data = body.model_dump(exclude_unset=True)

    user = service.update_user(user_id, update_data, current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Audit: log the update
    audit = AuditService(db)
    audit.log_update(
        entity_type="admin_user",
        entity_id=user_id,
        new_state=update_data,
        description=f"Updated user {user_id}",
    )

    # Get updated user with roles
    roles = service.get_user_roles(user_id)

    return UserUpdateResponse(
        data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "avatar_url": user.avatar_url,
            "timezone": user.timezone,
            "language": user.language,
            "last_login_at": user.last_login_at,
            "last_login_ip": user.last_login_ip,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "password_changed_at": user.password_changed_at,
            "email_verified_at": user.email_verified_at,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "profile": {
                "job_title": user.profile.job_title if user.profile else None,
                "phone": user.profile.phone if user.profile else None,
                "location": user.profile.location if user.profile else None,
                "company": user.profile.company if user.profile else None,
                "industry": user.profile.industry if user.profile else None,
            } if user.profile else None,
            "roles": roles,
        }
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Soft delete a user.

    Requires admin role.
    """
    service = UserManagementService(db)
    success = service.soft_delete_user(user_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    # Audit: log the deletion
    audit = AuditService(db)
    audit.log_delete(
        entity_type="admin_user",
        entity_id=user_id,
        description=f"Deleted user {user_id}",
    )

    return UserActionResponse(message="User deleted successfully")


@router.get("/{user_id}/timeline")
def get_user_timeline(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user action timeline.

    Requires admin role.
    """
    service = UserManagementService(db)
    user = service.get_user_detail(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    audit_service = AuditService(db)
    audit_logs = audit_service.get_user_history(
        user_id, limit=limit, offset=offset, action=action
    )

    total = audit_service.logs.count_by_user(user_id, action=action)
    has_more = (offset + limit) < total

    events = [UserTimelineEventOut(**map_audit_log_to_timeline_event(log)) for log in audit_logs]

    return UserTimelineResponse(
        events=events,
        total=total,
        has_more=has_more,
    )


@router.get("/{user_id}/sessions")
def get_user_sessions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user sessions.

    Requires admin role.
    """
    # TODO: Implement session retrieval when SessionService is created
    return {"items": [], "total": 0}
