"""PROCS User Management Schemas.

Pydantic schemas for PROCS user management endpoints.
Follows the response format defined in PROCS_Implementation.md Section 14.2.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# User List Schemas
# ---------------------------------------------------------------------------

class UserListOut(BaseModel):
    """User list item schema for PROCS user management."""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated user list response."""
    success: bool = True
    items: List[UserListOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


# ---------------------------------------------------------------------------
# User Detail Schemas
# ---------------------------------------------------------------------------

class UserRoleOut(BaseModel):
    """User role assignment schema."""
    id: str
    role_id: str
    role_name: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSessionOut(BaseModel):
    """User session schema."""
    id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserTimelineEventOut(BaseModel):
    """Single timeline event schema."""
    id: str
    icon: str
    title: str
    description: Optional[str] = None
    timestamp: str
    actor: str
    severity: str

    model_config = ConfigDict(from_attributes=True)


class UserTimelineResponse(BaseModel):
    """User timeline response schema."""
    success: bool = True
    events: list[UserTimelineEventOut] = []
    total: int = 0
    has_more: bool = False


class UserDetailOut(BaseModel):
    """Full user detail schema for PROCS user inspector."""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Profile
    profile: Optional[Dict[str, Any]] = None

    # Roles
    roles: List[UserRoleOut] = []

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    """User detail response."""
    success: bool = True
    data: UserDetailOut


# ---------------------------------------------------------------------------
# User Update Schemas
# ---------------------------------------------------------------------------

class UserUpdateRequest(BaseModel):
    """User update request schema."""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserUpdateResponse(BaseModel):
    """User update response schema."""
    success: bool = True
    data: UserDetailOut


# ---------------------------------------------------------------------------
# User Action Schemas
# ---------------------------------------------------------------------------

class UserActionResponse(BaseModel):
    """Generic user action response."""
    success: bool = True
    message: str


# ---------------------------------------------------------------------------
# User Stats Schema
# ---------------------------------------------------------------------------

class UserStatsOut(BaseModel):
    """User statistics schema."""
    total_users: int = 0
    active_users: int = 0
    verified_users: int = 0
    superuser_count: int = 0
    new_users_today: int = 0
    new_users_this_week: int = 0
    new_users_this_month: int = 0


class UserStatsResponse(BaseModel):
    """User stats response."""
    success: bool = True
    data: UserStatsOut
