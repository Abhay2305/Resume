"""RBAC domain schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Role Schemas
# ============================================================================

class RoleCreate(BaseModel):
    """Schema for creating a role."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_system: bool = False


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class RoleOut(BaseModel):
    """Role output schema."""
    id: str
    name: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleListResponse(BaseModel):
    """Role list response."""
    items: List[RoleOut] = []
    total: int = 0


# ============================================================================
# Permission Schemas
# ============================================================================

class PermissionOut(BaseModel):
    """Permission output schema."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RolePermissionOut(BaseModel):
    """Role-permission output schema."""
    id: str
    role_id: str
    permission_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignPermissionRequest(BaseModel):
    """Request to assign a permission to a role."""
    permission_id: str


class AssignPermissionResponse(BaseModel):
    """Response after assigning a permission."""
    success: bool = True
    message: str


# ============================================================================
# User Role Assignment Schemas
# ============================================================================

class AssignRoleRequest(BaseModel):
    """Request to assign a role to a user."""
    role_id: str
    expires_at: Optional[datetime] = None


class UserRoleAssignmentOut(BaseModel):
    """User role assignment output schema."""
    id: str
    user_id: str
    role_id: str
    role_name: Optional[str] = None
    assigned_by: Optional[str] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserRoleListResponse(BaseModel):
    """User role assignments list response."""
    items: List[UserRoleAssignmentOut] = []
    total: int = 0


# ============================================================================
# Admin Auth Schemas
# ============================================================================

class AdminLoginRequest(BaseModel):
    """Admin login request."""
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response."""
    access_token: str
    token_type: str = "bearer"
    admin: "AdminOut"


class AdminOut(BaseModel):
    """Admin user output schema."""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminChangePasswordRequest(BaseModel):
    """Admin password change request."""
    current_password: str
    new_password: str
    confirm_password: str


# Rebuild model with forward references
AdminLoginResponse.model_rebuild()
