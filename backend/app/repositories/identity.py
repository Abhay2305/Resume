"""Identity domain repositories.

Data access layer for Users, Profiles, Sessions, Devices, LoginHistory,
OAuthAccounts, Roles, Permissions, Organizations, and UserPreferences.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import and_

from ..models.identity import (
    Device,
    LoginHistory,
    OAuthAccount,
    Organization,
    OrganizationMember,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
    UserSession,
    UserPreference,
    Profile,
)
from .base import BaseRepository


# ---------------------------------------------------------------------------
# User Repository
# ---------------------------------------------------------------------------

class UserRepository(BaseRepository[User]):
    """Repository for User entity."""

    def __init__(self, db):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_active_user(self, id: str) -> Optional[User]:
        """Get active, non-deleted user."""
        return (
            self.db.query(User)
            .filter(User.id == id, User.is_active == True, User.deleted_at.is_(None))
            .first()
        )

    def get_active_users(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get active users with pagination."""
        return (
            self.db.query(User)
            .filter(User.is_active == True, User.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_last_login(self, user_id: str, ip_address: Optional[str] = None) -> User:
        """Update user's last login timestamp and IP."""
        user = self.get(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = ip_address
            user.failed_login_attempts = 0
            user.locked_until = None
            self.db.commit()
            self.db.refresh(user)
        return user

    def increment_failed_login(self, user_id: str, max_attempts: int = 5) -> User:
        """Increment failed login attempts. Lock account if threshold exceeded."""
        user = self.get(user_id)
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= max_attempts:
                # Lock for 30 minutes
                user.locked_until = datetime.utcnow() + datetime.timedelta(minutes=30)
            self.db.commit()
            self.db.refresh(user)
        return user

    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is currently locked."""
        user = self.get(user_id)
        if not user or not user.locked_until:
            return False
        if user.locked_until > datetime.utcnow():
            return True
        # Lock expired, clear it
        user.locked_until = None
        user.failed_login_attempts = 0
        self.db.commit()
        return False

    def verify_email(self, user_id: str) -> User:
        """Mark user email as verified."""
        user = self.get(user_id)
        if user:
            user.is_verified = True
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_password(self, user_id: str, hashed_password: str) -> User:
        """Update user password and track change time."""
        user = self.get(user_id)
        if user:
            user.hashed_password = hashed_password
            user.password_changed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user


# ---------------------------------------------------------------------------
# Profile Repository
# ---------------------------------------------------------------------------

class ProfileRepository(BaseRepository[Profile]):
    """Repository for Profile entity."""

    def __init__(self, db):
        super().__init__(Profile, db)

    def get_by_user_id(self, user_id: str) -> Optional[Profile]:
        """Get profile by user ID."""
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def get_or_create(self, user_id: str) -> Profile:
        """Get existing profile or create a new one."""
        profile = self.get_by_user_id(user_id)
        if not profile:
            profile = self.create({"user_id": user_id})
        return profile

    def update_fields(self, user_id: str, fields: Dict[str, Any]) -> Profile:
        """Update profile fields by user ID."""
        profile = self.get_by_user_id(user_id)
        if profile:
            for key, value in fields.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)
            self.db.commit()
            self.db.refresh(profile)
        return profile


# ---------------------------------------------------------------------------
# Session Repository
# ---------------------------------------------------------------------------

class SessionRepository(BaseRepository[UserSession]):
    """Repository for UserSession entity."""

    def __init__(self, db):
        super().__init__(UserSession, db)

    def get_by_token(self, token_hash: str) -> Optional[UserSession]:
        """Get session by token hash."""
        return (
            self.db.query(UserSession)
            .filter(UserSession.token_hash == token_hash)
            .first()
        )

    def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active (non-revoked, non-expired) sessions for a user."""
        return (
            self.db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.utcnow(),
            )
            .all()
        )

    def revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session."""
        session = self.get(session_id)
        if session:
            session.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user. Returns count revoked."""
        count = (
            self.db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False,
            )
            .update({"is_revoked": True})
        )
        self.db.commit()
        return count

    def cleanup_expired(self) -> int:
        """Delete expired sessions. Returns count deleted."""
        count = (
            self.db.query(UserSession)
            .filter(UserSession.expires_at < datetime.utcnow())
            .delete()
        )
        self.db.commit()
        return count

    def update_activity(self, session_id: str) -> UserSession:
        """Update session last activity timestamp."""
        session = self.get(session_id)
        if session:
            session.last_activity_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session


# ---------------------------------------------------------------------------
# Device Repository
# ---------------------------------------------------------------------------

class DeviceRepository(BaseRepository[Device]):
    """Repository for Device entity."""

    def __init__(self, db):
        super().__init__(Device, db)

    def get_by_fingerprint(
        self, user_id: str, fingerprint: str
    ) -> Optional[Device]:
        """Get device by user and fingerprint."""
        return (
            self.db.query(Device)
            .filter(
                Device.user_id == user_id,
                Device.fingerprint == fingerprint,
                Device.deleted_at.is_(None),
            )
            .first()
        )

    def get_user_devices(self, user_id: str) -> List[Device]:
        """Get all active devices for a user."""
        return (
            self.db.query(Device)
            .filter(Device.user_id == user_id, Device.deleted_at.is_(None))
            .order_by(Device.last_used_at.desc())
            .all()
        )

    def trust_device(self, device_id: str) -> Device:
        """Mark device as trusted."""
        device = self.get(device_id)
        if device:
            device.is_trusted = True
            self.db.commit()
            self.db.refresh(device)
        return device

    def update_last_used(self, device_id: str) -> Device:
        """Update device last used timestamp."""
        device = self.get(device_id)
        if device:
            device.last_used_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(device)
        return device


# ---------------------------------------------------------------------------
# Login History Repository
# ---------------------------------------------------------------------------

class LoginHistoryRepository(BaseRepository[LoginHistory]):
    """Repository for LoginHistory entity."""

    def __init__(self, db):
        super().__init__(LoginHistory, db)

    def get_by_user(
        self, user_id: str, limit: int = 50
    ) -> List[LoginHistory]:
        """Get login history for a user, most recent first."""
        return (
            self.db.query(LoginHistory)
            .filter(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent_by_email(
        self, email: str, limit: int = 10
    ) -> List[LoginHistory]:
        """Get recent login attempts by email."""
        return (
            self.db.query(LoginHistory)
            .filter(LoginHistory.email_used == email)
            .order_by(LoginHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def log_attempt(
        self,
        user_id: str,
        email: str,
        status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> LoginHistory:
        """Log a login attempt."""
        return self.create(
            {
                "user_id": user_id,
                "email_used": email,
                "status": status,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "device_id": device_id,
                "failure_reason": failure_reason,
            }
        )


# ---------------------------------------------------------------------------
# OAuth Account Repository
# ---------------------------------------------------------------------------

class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    """Repository for OAuthAccount entity."""

    def __init__(self, db):
        super().__init__(OAuthAccount, db)

    def get_by_provider(
        self, provider: str, provider_user_id: str
    ) -> Optional[OAuthAccount]:
        """Get OAuth account by provider and provider user ID."""
        return (
            self.db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
            .first()
        )

    def get_by_user_and_provider(
        self, user_id: str, provider: str
    ) -> Optional[OAuthAccount]:
        """Get OAuth account by user and provider."""
        return (
            self.db.query(OAuthAccount)
            .filter(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider,
            )
            .first()
        )

    def get_user_oauth_accounts(self, user_id: str) -> List[OAuthAccount]:
        """Get all OAuth accounts for a user."""
        return (
            self.db.query(OAuthAccount)
            .filter(OAuthAccount.user_id == user_id)
            .all()
        )

    def link_account(
        self, user_id: str, provider: str, provider_data: Dict[str, Any]
    ) -> OAuthAccount:
        """Link an OAuth account to a user."""
        existing = self.get_by_user_and_provider(user_id, provider)
        if existing:
            # Update existing account
            for key, value in provider_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create({"user_id": user_id, "provider": provider, **provider_data})

    def unlink_account(self, user_id: str, provider: str) -> bool:
        """Unlink an OAuth account from a user."""
        account = self.get_by_user_and_provider(user_id, provider)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False


# ---------------------------------------------------------------------------
# Role Repository
# ---------------------------------------------------------------------------

class RoleRepository(BaseRepository[Role]):
    """Repository for Role entity."""

    def __init__(self, db):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).filter(Role.name == name).first()

    def get_active_roles(self) -> List[Role]:
        """Get all active roles."""
        return (
            self.db.query(Role)
            .filter(Role.is_active == True, Role.deleted_at.is_(None))
            .all()
        )

    def get_system_roles(self) -> List[Role]:
        """Get all system (non-deletable) roles."""
        return (
            self.db.query(Role)
            .filter(Role.is_system == True, Role.deleted_at.is_(None))
            .all()
        )

    def create_system_role(
        self, name: str, description: Optional[str] = None
    ) -> Role:
        """Create a system role that cannot be deleted."""
        return self.create({
            "name": name,
            "description": description,
            "is_system": True,
        })

    def add_permission(self, role_id: str, permission_id: str) -> RolePermission:
        """Add a permission to a role."""
        existing = (
            self.db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
            .first()
        )
        if existing:
            return existing
        return self.create(
            RolePermission(role_id=role_id, permission_id=permission_id)
        )


# ---------------------------------------------------------------------------
# Permission Repository
# ---------------------------------------------------------------------------

class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission entity."""

    def __init__(self, db):
        super().__init__(Permission, db)

    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == name).first()

    def get_by_resource_action(
        self, resource: str, action: str
    ) -> Optional[Permission]:
        """Get permission by resource and action."""
        return (
            self.db.query(Permission)
            .filter(
                Permission.resource == resource,
                Permission.action == action,
            )
            .first()
        )

    def get_resource_permissions(self, resource: str) -> List[Permission]:
        """Get all permissions for a resource."""
        return (
            self.db.query(Permission)
            .filter(Permission.resource == resource)
            .all()
        )


# ---------------------------------------------------------------------------
# UserRole Repository
# ---------------------------------------------------------------------------

class UserRoleRepository(BaseRepository[UserRole]):
    """Repository for UserRole junction entity."""

    def __init__(self, db):
        super().__init__(UserRole, db)

    def get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get all active role assignments for a user."""
        return (
            self.db.query(UserRole)
            .filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                UserRole.expires_at.is_(None) | (UserRole.expires_at > datetime.utcnow()),
            )
            .all()
        )

    def assign_role(
        self,
        user_id: str,
        role_id: str,
        assigned_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserRole:
        """Assign a role to a user."""
        existing = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )
        if existing:
            existing.is_active = True
            existing.expires_at = expires_at
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create({
            "user_id": user_id,
            "role_id": role_id,
            "assigned_by": assigned_by,
            "expires_at": expires_at,
        })

    def revoke_role(self, user_id: str, role_id: str) -> bool:
        """Revoke a role from a user."""
        assignment = (
            self.db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )
        if assignment:
            assignment.is_active = False
            self.db.commit()
            return True
        return False


# ---------------------------------------------------------------------------
# Organization Repository
# ---------------------------------------------------------------------------

class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization entity."""

    def __init__(self, db):
        super().__init__(Organization, db)

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        return (
            self.db.query(Organization)
            .filter(Organization.slug == slug, Organization.deleted_at.is_(None))
            .first()
        )

    def get_by_owner(self, owner_id: str) -> List[Organization]:
        """Get organizations owned by a user."""
        return (
            self.db.query(Organization)
            .filter(Organization.owner_id == owner_id, Organization.deleted_at.is_(None))
            .all()
        )

    def get_user_organizations(self, user_id: str) -> List[Organization]:
        """Get all organizations a user belongs to."""
        return (
            self.db.query(Organization)
            .join(OrganizationMember)
            .filter(
                OrganizationMember.user_id == user_id,
                OrganizationMember.is_active == True,
                Organization.deleted_at.is_(None),
            )
            .all()
        )

    def add_member(
        self,
        organization_id: str,
        user_id: str,
        role_id: Optional[str] = None,
        invited_by: Optional[str] = None,
    ) -> OrganizationMember:
        """Add a member to an organization."""
        existing = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )
        if existing:
            existing.is_active = True
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(
            OrganizationMember,
            {
                "organization_id": organization_id,
                "user_id": user_id,
                "role_id": role_id,
                "invited_by": invited_by,
            },
        )

    def remove_member(self, organization_id: str, user_id: str) -> bool:
        """Remove a member from an organization."""
        member = (
            self.db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )
        if member:
            member.is_active = False
            self.db.commit()
            return True
        return False


# ---------------------------------------------------------------------------
# UserPreference Repository
# ---------------------------------------------------------------------------

class UserPreferenceRepository(BaseRepository[UserPreference]):
    """Repository for UserPreference entity."""

    def __init__(self, db):
        super().__init__(UserPreference, db)

    def get_by_user_category(
        self, user_id: str, category: str
    ) -> List[UserPreference]:
        """Get all preferences in a category for a user."""
        return (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
            )
            .all()
        )

    def get_value(
        self, user_id: str, category: str, key: str
    ) -> Optional[str]:
        """Get a specific preference value."""
        pref = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
            .first()
        )
        return pref.value if pref else None

    def set_value(
        self, user_id: str, category: str, key: str, value: str
    ) -> UserPreference:
        """Set a preference value (create or update)."""
        pref = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
            .first()
        )
        if pref:
            pref.value = value
            self.db.commit()
            self.db.refresh(pref)
            return pref
        return self.create({
            "user_id": user_id,
            "category": category,
            "key": key,
            "value": value,
        })

    def set_bulk(
        self, user_id: str, category: str, preferences: Dict[str, str]
    ) -> List[UserPreference]:
        """Set multiple preferences in a category."""
        results = []
        for key, value in preferences.items():
            results.append(self.set_value(user_id, category, key, value))
        return results

    def delete_value(self, user_id: str, category: str, key: str) -> bool:
        """Delete a specific preference."""
        pref = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
                UserPreference.key == key,
            )
            .first()
        )
        if pref:
            self.db.delete(pref)
            self.db.commit()
            return True
        return False

    def delete_category(self, user_id: str, category: str) -> int:
        """Delete all preferences in a category. Returns count deleted."""
        count = (
            self.db.query(UserPreference)
            .filter(
                UserPreference.user_id == user_id,
                UserPreference.category == category,
            )
            .delete()
        )
        self.db.commit()
        return count


# ---------------------------------------------------------------------------
# Factory function for easy access
# ---------------------------------------------------------------------------

def get_repositories(db):
    """Get all identity repositories for a database session."""
    return {
        "users": UserRepository(db),
        "profiles": ProfileRepository(db),
        "sessions": SessionRepository(db),
        "devices": DeviceRepository(db),
        "login_history": LoginHistoryRepository(db),
        "oauth_accounts": OAuthAccountRepository(db),
        "roles": RoleRepository(db),
        "permissions": PermissionRepository(db),
        "user_roles": UserRoleRepository(db),
        "organizations": OrganizationRepository(db),
        "preferences": UserPreferenceRepository(db),
    }
