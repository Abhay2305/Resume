"""Admin Authentication Router.

Provides admin-specific authentication endpoints separate from user auth.
Admin login requires admin privileges and uses role-based access control.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.rbac import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminOut,
    AdminChangePasswordRequest,
)
from ..schemas import MessageResponse
from ..auth import (
    verify_password,
    create_access_token,
    get_current_user,
    require_auth,
    require_admin,
    validate_password_strength,
    get_password_hash,
)
from ..services.audit_service import AuditService

router = APIRouter(prefix="/auth/admin", tags=["Admin Authentication"])
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Account lockout configuration
# ---------------------------------------------------------------------------

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


def _is_account_locked(user: User) -> bool:
    """Check if the user account is currently locked."""
    if user.locked_until and user.locked_until > datetime.utcnow():
        return True
    return False


def _record_failed_login(user: User, db: Session):
    """Increment failed login attempts and lock if threshold reached."""
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    db.commit()


def _reset_failed_login(user: User, db: Session):
    """Reset failed login attempts after successful login."""
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()


# ---------------------------------------------------------------------------
# POST /api/auth/admin/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=AdminLoginResponse)
def admin_login(request: AdminLoginRequest, req: Request, db: Session = Depends(get_db)):
    """Admin login endpoint.
    
    Validates admin credentials and returns JWT token.
    Requires user to be superuser or have admin role.
    """
    user = db.query(User).filter(User.email == request.email).first()
    audit = AuditService(db)

    # Check account lockout
    if user and _is_account_locked(user):
        # Log access denied for locked account
        audit.log_security_event(
            action="access_denied",
            description="Account is temporarily locked",
            user_id=user.id,
            entity_type="admin_auth",
            entity_id=user.id,
            ip_address=req.client.host if req.client else None,
            user_agent=req.headers.get("user-agent"),
            success=False,
            error_message="Account locked due to too many failed attempts",
        )
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed login attempts.",
        )

    # Verify user exists and password is correct
    if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
        if user:
            _record_failed_login(user, db)
            # Log failed login attempt
            audit.log_login(
                user_id=user.id,
                success=False,
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get("user-agent"),
                error_message="Invalid credentials",
            )
        else:
            # Log attempt with non-existent email
            audit.log_security_event(
                action="login_failed",
                description="Login attempt with non-existent email",
                entity_type="admin_auth",
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get("user-agent"),
                success=False,
                error_message="Invalid credentials",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user has admin privileges
    if not user.is_superuser:
        # Check if user has admin role
        from ..models import UserRole, Role
        
        has_admin_role = (
            db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(
                UserRole.user_id == user.id,
                UserRole.is_active == True,
                Role.name.in_(["admin", "superadmin"]),
            )
            .first()
        )
        
        if not has_admin_role:
            # Log access denied for non-admin
            audit.log_security_event(
                action="access_denied",
                description="Non-admin user attempted admin login",
                user_id=user.id,
                entity_type="admin_auth",
                entity_id=user.id,
                ip_address=req.client.host if req.client else None,
                user_agent=req.headers.get("user-agent"),
                success=False,
                error_message="Admin privileges required",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )

    # Reset failed attempts on successful login
    _reset_failed_login(user, db)

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create access token with admin claim
    access_token = create_access_token(
        data={"sub": user.id, "is_admin": True}
    )

    # Log successful login
    audit.log_login(
        user_id=user.id,
        success=True,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
    )

    # Build admin response
    admin_data = AdminOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )

    logger.info("Admin login successful: %s", user.email)
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        admin=admin_data,
    )


# ---------------------------------------------------------------------------
# GET /api/auth/admin/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=AdminOut)
def admin_me(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Get current admin user information.
    
    Returns admin profile with current authentication status.
    Requires admin privileges.
    """
    return AdminOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
    )


# ---------------------------------------------------------------------------
# POST /api/auth/admin/logout
# ---------------------------------------------------------------------------

@router.post("/logout", response_model=MessageResponse)
def admin_logout(
    req: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Admin logout endpoint.
    
    Client-side token removal.
    In production, implement server-side token revocation.
    """
    audit = AuditService(db)
    audit.log_logout(
        user_id=current_user.id,
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("user-agent"),
    )

    return MessageResponse(message="Admin logged out successfully")


# ---------------------------------------------------------------------------
# POST /api/auth/admin/change-password
# ---------------------------------------------------------------------------

@router.post("/change-password", response_model=MessageResponse)
def admin_change_password(
    request: AdminChangePasswordRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Change admin password.
    
    Requires current password verification and password strength validation.
    """
    audit = AuditService(db)

    # Verify passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match",
        )

    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Validate new password strength
    pw_check = validate_password_strength(request.new_password)
    if not pw_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(pw_check["errors"]),
        )

    # Check if new password is different from current
    if verify_password(request.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be different from current password",
        )

    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    current_user.password_changed_at = datetime.utcnow()
    current_user.failed_login_attempts = 0
    current_user.locked_until = None
    db.commit()

    # Audit: log the password change
    audit.log_security_event(
        action="password_changed",
        description=f"Admin password changed for {current_user.email}",
        user_id=current_user.id,
        entity_type="admin_auth",
        entity_id=current_user.id,
        success=True,
    )

    logger.info("Admin password changed: %s", current_user.email)
    return MessageResponse(message="Password changed successfully")
