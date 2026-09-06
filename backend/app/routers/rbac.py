"""RBAC Management Router.

Provides endpoints for managing roles, permissions, and user role assignments.
All endpoints require admin or superadmin role.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    RoleOut,
    RoleListResponse,
    PermissionOut,
    AssignPermissionRequest,
    AssignPermissionResponse,
    AssignRoleRequest,
    UserRoleAssignmentOut,
    UserRoleListResponse,
)
from ..schemas import MessageResponse
from ..auth import require_auth
from ..services.rbac_service import RBACService

router = APIRouter(prefix="/rbac", tags=["RBAC Management"])
logger = logging.getLogger(__name__)


def _require_admin(current_user: User = Depends(require_auth), db: Session = Depends(get_db)) -> User:
    """Verify user has admin or superadmin privileges."""
    if current_user.is_superuser:
        return current_user

    from ..models import UserRole, Role
    
    has_admin_role = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == current_user.id,
            UserRole.is_active == True,
            Role.name.in_(["admin", "superadmin"]),
        )
        .first()
    )

    if not has_admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


# ---------------------------------------------------------------------------
# Role Endpoints
# ---------------------------------------------------------------------------

@router.get("/roles", response_model=RoleListResponse)
def list_roles(
    include_inactive: bool = False,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """List all roles."""
    service = RBACService(db)
    roles = service.list_roles(include_inactive=include_inactive)
    return RoleListResponse(items=roles, total=len(roles))


@router.get("/roles/{role_id}", response_model=RoleOut)
def get_role(
    role_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Get role by ID."""
    service = RBACService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return role


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Create a new role."""
    service = RBACService(db)
    try:
        role = service.create_role(
            name=role_in.name,
            description=role_in.description,
            is_system=role_in.is_system,
            user_id=current_user.id,
        )
        logger.info("Admin %s created role %s", current_user.email, role.name)
        return role
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/roles/{role_id}", response_model=RoleOut)
def update_role(
    role_id: str,
    role_in: RoleUpdate,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Update a role."""
    service = RBACService(db)
    try:
        role = service.update_role(
            role_id=role_id,
            name=role_in.name,
            description=role_in.description,
            user_id=current_user.id,
        )
        logger.info("Admin %s updated role %s", current_user.email, role.name)
        return role
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/roles/{role_id}", response_model=MessageResponse)
def delete_role(
    role_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Delete a role (soft delete)."""
    service = RBACService(db)
    try:
        service.delete_role(role_id, user_id=current_user.id)
        logger.info("Admin %s deleted role %s", current_user.email, role_id)
        return MessageResponse(message="Role deleted successfully")
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ---------------------------------------------------------------------------
# Permission Endpoints
# ---------------------------------------------------------------------------

@router.get("/permissions")
def list_permissions(
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """List all permissions."""
    service = RBACService(db)
    permissions = service.list_permissions()
    return {"items": permissions, "total": len(permissions)}


@router.get("/roles/{role_id}/permissions")
def get_role_permissions(
    role_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Get all permissions for a role."""
    service = RBACService(db)
    try:
        permissions = service.get_role_permissions(role_id)
        return {"items": permissions, "total": len(permissions)}
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )


@router.post("/roles/{role_id}/permissions", response_model=AssignPermissionResponse)
def add_permission_to_role(
    role_id: str,
    request: AssignPermissionRequest,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Add a permission to a role."""
    service = RBACService(db)
    try:
        service.add_permission_to_role(role_id, request.permission_id, user_id=current_user.id)
        logger.info(
            "Admin %s added permission %s to role %s",
            current_user.email,
            request.permission_id,
            role_id,
        )
        return AssignPermissionResponse(
            success=True,
            message="Permission added to role successfully",
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=MessageResponse,
)
def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Remove a permission from a role."""
    service = RBACService(db)
    result = service.remove_permission_from_role(role_id, permission_id, user_id=current_user.id)
    if result:
        logger.info(
            "Admin %s removed permission %s from role %s",
            current_user.email,
            permission_id,
            role_id,
        )
    return MessageResponse(message="Permission removed from role successfully")


# ---------------------------------------------------------------------------
# User Role Assignment Endpoints
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/roles", response_model=UserRoleListResponse)
def get_user_roles(
    user_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Get all roles for a user."""
    service = RBACService(db)
    assignments = service.get_user_roles(user_id)
    
    result = []
    for assignment, role in assignments:
        result.append(
            UserRoleAssignmentOut(
                id=assignment.id,
                user_id=assignment.user_id,
                role_id=assignment.role_id,
                role_name=role.name,
                assigned_by=assignment.assigned_by,
                assigned_at=assignment.assigned_at,
                expires_at=assignment.expires_at,
                is_active=assignment.is_active,
            )
        )
    
    return UserRoleListResponse(items=result, total=len(result))


@router.post(
    "/users/{user_id}/roles",
    response_model=UserRoleAssignmentOut,
    status_code=status.HTTP_201_CREATED,
)
def assign_role_to_user(
    user_id: str,
    request: AssignRoleRequest,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Assign a role to a user."""
    service = RBACService(db)
    try:
        assignment = service.assign_role(
            user_id=user_id,
            role_id=request.role_id,
            assigned_by=current_user.id,
            expires_at=request.expires_at,
        )
        
        # Get role name for response
        role = service.get_role(request.role_id)
        role_name = role.name if role else None
        
        logger.info(
            "Admin %s assigned role %s to user %s",
            current_user.email,
            request.role_id,
            user_id,
        )
        
        return UserRoleAssignmentOut(
            id=assignment.id,
            user_id=assignment.user_id,
            role_id=assignment.role_id,
            role_name=role_name,
            assigned_by=assignment.assigned_by,
            assigned_at=assignment.assigned_at,
            expires_at=assignment.expires_at,
            is_active=assignment.is_active,
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    response_model=MessageResponse,
)
def revoke_role_from_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    """Revoke a role from a user."""
    service = RBACService(db)
    result = service.revoke_role(user_id, role_id, revoked_by=current_user.id)
    if result:
        logger.info(
            "Admin %s revoked role %s from user %s",
            current_user.email,
            role_id,
            user_id,
        )
    return MessageResponse(message="Role revoked from user successfully")
