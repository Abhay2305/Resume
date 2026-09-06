import logging
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import User, Profile, Subscription, OAuthAccount
from ..schemas import (
    UserCreate, UserLogin, UserOut, Token,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse,
    ChangePasswordRequest, DeleteAccountRequest, UserLoginWithRememberMe,
    UserOutWithVerification,
)
from ..auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_auth, validate_password_strength,
    create_reset_token, verify_reset_token, generate_reset_token,
    create_verification_token, verify_verification_token,
    generate_verification_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

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
# POST /api/auth/register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Validate password strength
    pw_check = validate_password_strength(user_in.password)
    if not pw_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(pw_check["errors"]),
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered.",
        )

    # Hash password and save user
    hashed_pw = get_password_hash(user_in.password)
    
    # Generate verification token
    verification_token = generate_verification_token()
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires_at=token_expires,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create an associated profile
    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)

    # Create free subscription
    new_sub = Subscription(user_id=new_user.id, plan_type="free", status="active")
    db.add(new_sub)

    db.commit()

    # Send verification email (in production, use a task queue)
    from ..services.email_templates import verification_email
    from ..auth import create_verification_token as create_token_for_url
    
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={verification_token}"
    email_template = verification_email(user_in.full_name, verification_url)
    
    # TODO: Integrate with email sending service (SendGrid, AWS SES, etc.)
    logger.info("Verification email for %s: %s", new_user.email, verification_url)
    logger.info("Email subject: %s", email_template['subject'])

    return new_user


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=Token)
def login_user(user_in: UserLoginWithRememberMe, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()

    # Check account lockout
    if user and _is_account_locked(user):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to too many failed login attempts. Please try again later.",
        )

    # Verify user exists and password is correct
    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        if user:
            _record_failed_login(user, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset failed attempts on successful login
    _reset_failed_login(user, db)

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": user.id}, remember_me=user_in.remember_me)
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserOutWithVerification)
def read_current_user(current_user: User = Depends(require_auth), db: Session = Depends(get_db)):
    # Determine login provider
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.user_id == current_user.id,
        OAuthAccount.provider == "google"
    ).first()
    
    login_provider = "google" if oauth_account else "email"
    
    # Create response with additional fields
    user_data = UserOutWithVerification.model_validate(current_user)
    user_data.login_provider = login_provider
    
    return user_data


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------

@router.post("/logout", response_model=MessageResponse)
def logout_user(current_user: User = Depends(get_current_user)):
    """Logout endpoint. Client-side token removal.
    
    In a session-based system this would revoke the server-side session.
    With stateless JWTs, the client simply discards the token.
    This endpoint exists for consistency and future server-side revocation.
    """
    return MessageResponse(message="Successfully logged out")


# ---------------------------------------------------------------------------
# POST /api/auth/forgot-password
# ---------------------------------------------------------------------------

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset link.
    
    Always returns success to prevent email enumeration.
    If the email exists, a reset token is generated (and would be sent via email).
    """
    user = db.query(User).filter(User.email == request.email).first()

    if user and user.hashed_password:
        # Generate reset token
        reset_token = create_reset_token(user.email)

        # Store hashed token for verification (optional extra security)
        # For MVP: token is a JWT with built-in expiry, so we don't need to store it.
        # In production, store the token hash in DB and verify on reset.

        # TODO: Send email with reset link containing the token
        # Example: send_reset_email(user.email, reset_token)
        logger.info("Password reset token for %s: %s", user.email, reset_token)

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


# ---------------------------------------------------------------------------
# POST /api/auth/reset-password
# ---------------------------------------------------------------------------

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid reset token."""
    # Validate passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match",
        )

    # Validate password strength
    pw_check = validate_password_strength(request.new_password)
    if not pw_check["valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="; ".join(pw_check["errors"]),
        )

    # Verify reset token
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    return MessageResponse(message="Password has been reset successfully")


# -----------------------------------------------------------------------
# Google OAuth
# -----------------------------------------------------------------------

class GoogleAuthRequest(BaseModel):
    """Google OAuth credential from frontend."""
    credential: str  # Google ID token


@router.post("/google", response_model=Token)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth.
    
    Verifies the Google ID token cryptographically using google-auth,
    then creates or links the user account via OAuthAccount.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        if not GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google client ID not configured")

        # Cryptographically verify the Google ID token
        # Validates: signature, audience, issuer, expiration
        idinfo = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")
        google_user_id = idinfo.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="No email in Google credential")
        if not google_user_id:
            raise HTTPException(status_code=400, detail="No subject in Google credential")

        # Check if OAuthAccount already exists for this Google user
        oauth_account = (
            db.query(OAuthAccount)
            .filter(OAuthAccount.provider == "google", OAuthAccount.provider_user_id == google_user_id)
            .first()
        )

        if oauth_account:
            # Existing Google user — load linked user
            user = db.query(User).filter(User.id == oauth_account.user_id).first()
            if not user:
                raise HTTPException(status_code=400, detail="Linked user not found")
            # Update avatar/name from Google profile
            user.avatar_url = picture or user.avatar_url
            user.full_name = name or user.full_name
            db.commit()
        else:
            # New Google user — check if email already exists
            user = db.query(User).filter(User.email == email).first()

            if user:
                # Email exists — link OAuthAccount to existing user
                pass
            else:
                # Brand new user — create everything
                user = User(
                    email=email,
                    full_name=name,
                    avatar_url=picture,
                    is_verified=True,
                    hashed_password=None,
                )
                db.add(user)
                db.flush()

                profile = Profile(user_id=user.id)
                db.add(profile)

                sub = Subscription(user_id=user.id, plan_type="free", status="active")
                db.add(sub)

            # Create OAuthAccount linkage
            oauth = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_user_id=google_user_id,
                provider_email=email,
                provider_name=name,
                provider_avatar_url=picture,
            )
            db.add(oauth)
            db.commit()

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        # Generate platform JWT
        access_token = create_access_token(data={"sub": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except ValueError as e:
        # google-auth raises ValueError for invalid tokens
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")


# -----------------------------------------------------------------------
# POST /api/auth/send-verification
# -----------------------------------------------------------------------

@router.post("/send-verification", response_model=MessageResponse)
def send_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send verification email to the current user.
    
    Prevents abuse with a 5-minute cooldown between requests.
    Generates a new token and invalidates any previous one.
    """
    # Check if already verified
    if current_user.is_verified and current_user.email_verified_at:
        return MessageResponse(message="Email is already verified")
    
    # Check cooldown (5 minutes between requests)
    if current_user.verification_token_expires_at:
        cooldown_remaining = (current_user.verification_token_expires_at - datetime.utcnow()).total_seconds()
        if cooldown_remaining > 24 * 60 * 60 - 5 * 60:  # If token was created less than 5 minutes ago
            return MessageResponse(message="Please wait before requesting another verification email")
    
    # Generate new verification token (invalidates old one)
    verification_token = generate_verification_token()
    token_expires = datetime.utcnow() + timedelta(hours=24)
    
    current_user.verification_token = verification_token
    current_user.verification_token_expires_at = token_expires
    db.commit()
    
    # Send verification email
    from ..services.email_templates import verification_email
    
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={verification_token}"
    email_template = verification_email(current_user.full_name, verification_url)
    
    # TODO: Integrate with email sending service
    logger.info("Verification email for %s: %s", current_user.email, verification_url)
    
    return MessageResponse(message="Verification email sent successfully")


# -----------------------------------------------------------------------
# GET /api/auth/verify-email
# -----------------------------------------------------------------------

@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using the token from the verification email."""
    # Find user by verification token
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )
    
    # Check if token has expired
    if user.verification_token_expires_at and user.verification_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one.",
        )
    
    # Check if already verified
    if user.is_verified and user.email_verified_at:
        return MessageResponse(message="Email is already verified")
    
    # Verify the email
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.verification_token = None
    user.verification_token_expires_at = None
    db.commit()
    
    return MessageResponse(message="Email verified successfully")


# -----------------------------------------------------------------------
# POST /api/auth/change-password
# -----------------------------------------------------------------------

@router.post("/change-password", response_model=MessageResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user.
    
    Requires current password verification and password strength validation.
    """
    # Verify passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match",
        )
    
    # Check if user has a password (OAuth-only users don't)
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account uses Google sign-in. Please set a password through the settings page.",
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
    
    return MessageResponse(message="Password changed successfully")


# -----------------------------------------------------------------------
# DELETE /api/auth/account
# -----------------------------------------------------------------------

@router.delete("/account", response_model=MessageResponse)
def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete user account.
    
    Requires password verification and explicit confirmation.
    Preserves audit logs and does not immediately delete resumes.
    """
    # Verify confirmation text
    if request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please type 'DELETE' to confirm account deletion",
        )
    
    # Verify password
    if current_user.hashed_password and not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    # Soft delete - deactivate account
    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()
    current_user.email = f"deleted_{current_user.id}@deleted.local"  # Anonymize email
    db.commit()
    
    # Send deletion confirmation email
    from ..services.email_templates import account_deletion_email
    email_template = account_deletion_email(current_user.full_name)
    
    # TODO: Integrate with email sending service
    logger.info("Account deletion email for deleted user")
    
    return MessageResponse(message="Account has been deactivated successfully")


# -----------------------------------------------------------------------
# GET /api/auth/settings
# -----------------------------------------------------------------------

@router.get("/settings")
def get_auth_settings(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get authentication settings for the current user.
    
    Returns verification status, login provider, and security info.
    """
    # Determine login provider
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.user_id == current_user.id,
        OAuthAccount.provider == "google"
    ).first()
    
    login_provider = "google" if oauth_account else "email"
    
    # Check if user has password
    has_password = current_user.hashed_password is not None
    
    return {
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "email_verified_at": current_user.email_verified_at.isoformat() if current_user.email_verified_at else None,
        "login_provider": login_provider,
        "has_password": has_password,
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "password_changed_at": current_user.password_changed_at.isoformat() if current_user.password_changed_at else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }
