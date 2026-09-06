import os
import re
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .context import get_request_id, get_user_id
from .exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# Configuration
_secret_key = os.getenv("JWT_SECRET_KEY")
if not _secret_key:
    logger.critical(
        "JWT_SECRET_KEY environment variable not set. "
        "Using insecure fallback for development only. "
        "Set JWT_SECRET_KEY in production."
    )
    _secret_key = "super_secret_resume_key_jwt_token_123456789"
SECRET_KEY = _secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours
ACCESS_TOKEN_REMEMBER_ME_MINUTES = 60 * 24 * 30  # 30 days for remember me
RESET_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes for password reset
VERIFICATION_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for email verification

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# ---------------------------------------------------------------------------
# Password utilities
# ---------------------------------------------------------------------------

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash.

    Returns True if the password matches, False otherwise.
    Never raises — catches all hashing errors to prevent internal
    exceptions (e.g. bcrypt version incompatibilities) from leaking
    as HTTP 500 to the client.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        logger.warning("Password verification failed due to hashing error", exc_info=True)
        return False

def get_password_hash(password):
    """Hash a password using bcrypt.

    Raises ValueError if the password exceeds bcrypt's 72-byte limit,
    or if the hashing backend is misconfigured.  Callers should catch
    this and convert to an appropriate HTTP error.
    """
    try:
        return pwd_context.hash(password)
    except ValueError:
        raise
    except Exception:
        logger.error("Password hashing failed due to backend error", exc_info=True)
        raise ValueError("Password hashing is temporarily unavailable")

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password meets security requirements.
    
    Returns dict with 'valid' bool and 'errors' list.
    Requirements: min 8 chars, uppercase, lowercase, number.
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    return {"valid": len(errors) == 0, "errors": errors}

def generate_reset_token() -> str:
    """Generate a cryptographically secure reset token."""
    return secrets.token_urlsafe(48)

def create_reset_token(email: str) -> str:
    """Create a JWT token for password reset with short expiry."""
    to_encode = {"sub": email, "type": "reset"}
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> Optional[str]:
    """Verify a reset token and return the email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            return None
        email = payload.get("sub")
        return email
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Email verification utilities
# ---------------------------------------------------------------------------

def generate_verification_token() -> str:
    """Generate a cryptographically secure email verification token."""
    return secrets.token_urlsafe(48)


def create_verification_token(email: str) -> str:
    """Create a JWT token for email verification with 24-hour expiry."""
    to_encode = {"sub": email, "type": "verification"}
    expire = datetime.utcnow() + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_verification_token(token: str) -> Optional[str]:
    """Verify an email verification token and return the email if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "verification":
            return None
        email = payload.get("sub")
        return email
    except JWTError:
        return None

# ---------------------------------------------------------------------------
# JWT utilities
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, remember_me: bool = False):
    """Create a JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Custom expiration time (overrides remember_me)
        remember_me: If True, token expires in 30 days instead of 24 hours
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif remember_me:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_REMEMBER_ME_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return the payload dict.
    
    Used by middleware for extracting user context from requests.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Get the current authenticated user.
    
    Returns None when no token is provided (guest access).
    Raises 401 when a token is provided but invalid or expired.
    This enables guest-first workflows while maintaining security.
    """
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    return user


def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Dependency that requires authentication.
    
    Use this for endpoints that MUST have a logged-in user.
    Returns the user if authenticated, raises 401 otherwise.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(role_name: str):
    """Dependency factory that requires a specific role.
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(require_role("admin"))):
            ...
    
    Also checks is_superuser as a bypass for super administrators.
    """
    def _check_role(current_user: User = Depends(require_auth)) -> User:
        # Superusers bypass role checks
        if current_user.is_superuser:
            return current_user
        
        # Check user's roles
        from .models import UserRole, Role
        from .database import SessionLocal
        
        db = SessionLocal()
        try:
            user_roles = (
                db.query(Role.name)
                .join(UserRole, UserRole.role_id == Role.id)
                .filter(UserRole.user_id == current_user.id, UserRole.is_active == True)
                .all()
            )
            role_names = [r.name for r in user_roles]
            
            if role_name not in role_names:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role_name}' required",
                )
            return current_user
        finally:
            db.close()
    
    return _check_role


def require_permission(resource: str, action: str):
    """Dependency factory that requires a specific permission.
    
    Usage:
        @router.delete("/resumes/{id}")
        def delete_resume(
            id: str,
            user: User = Depends(require_permission("resume", "delete"))
        ):
            ...
    
    Also checks is_superuser as a bypass for super administrators.
    """
    def _check_permission(current_user: User = Depends(require_auth)) -> User:
        # Superusers bypass permission checks
        if current_user.is_superuser:
            return current_user
        
        from .models import UserRole, RolePermission, Permission
        from .database import SessionLocal
        
        db = SessionLocal()
        try:
            has_permission = (
                db.query(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(UserRole, UserRole.role_id == RolePermission.role_id)
                .filter(
                    UserRole.user_id == current_user.id,
                    UserRole.is_active == True,
                    Permission.resource == resource,
                    Permission.action == action,
                )
                .first()
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{resource}:{action}' required",
                )
            return current_user
        finally:
            db.close()
    
    return _check_permission


def require_admin(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """Dependency that requires admin authorization.
    
    Validates:
    1. User is authenticated (not None)
    2. User is an administrator (is_superuser=True)
    
    Returns:
        The authenticated admin user
        
    Raises:
        AuthenticationError (401): If user is not authenticated
        AuthorizationError (403): If user is authenticated but not an admin
    """
    request_id = get_request_id()
    
    # Step 1: Check authentication
    if current_user is None:
        logger.warning(
            "Admin authorization failed: not authenticated (request_id=%s)",
            request_id,
        )
        raise AuthenticationError(
            message="Authentication required",
            details={"reason": "No valid authentication token provided"},
        )
    
    # Step 2: Check admin status
    if not current_user.is_superuser:
        logger.warning(
            "Admin authorization failed: not an administrator (user_id=%s, request_id=%s)",
            current_user.id,
            request_id,
        )
        raise AuthorizationError(
            message="Admin access required",
            details={
                "reason": "User is not an administrator",
                "user_id": current_user.id,
            },
        )
    
    return current_user
