"""Identity domain models.

Contains the complete identity management system for the AI Career Intelligence
Platform. This includes user accounts, profiles, sessions, devices, login
history, OAuth accounts, roles, permissions, organizations, and user preferences.

Design Principles:
- All primary keys are UUID strings (36 chars)
- Timestamps (created_at, updated_at) on all mutable entities
- Soft delete (deleted_at) on entities that should be recoverable
- metadata_json for additive evolution without migrations
- Proper foreign keys with CASCADE/SET NULL as appropriate
- Indexes on frequently queried columns
- UNIQUE constraints where business logic requires it
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import (
    MetadataMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    """User account entity.

    The central identity record. Holds authentication credentials, account
    status, and links to all domain-specific user data. Designed to support
    multiple authentication methods (password, OAuth) and account lifecycle
    management (verification, locking, deactivation).
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # nullable for OAuth-only users
    full_name = Column(String(255), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Profile fields
    avatar_url = Column(String(512), nullable=True)
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), default="en", nullable=False)

    # Security fields
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 max length
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)

    # Email verification fields
    email_verified_at = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True, index=True)
    verification_token_expires_at = Column(DateTime, nullable=True)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)  # JSON string for SQLite compat

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)  # Soft delete

    # Relationships
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    devices = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    login_history = relationship(
        "LoginHistory", back_populates="user", cascade="all, delete-orphan"
    )
    oauth_accounts = relationship(
        "OAuthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[UserRole.user_id]",
    )
    preferences = relationship(
        "UserPreference", back_populates="user", cascade="all, delete-orphan"
    )
    # Cross-domain relationships (referenced by other domains)
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    cover_letters = relationship(
        "CoverLetter", back_populates="user", cascade="all, delete-orphan"
    )
    ai_requests = relationship(
        "AIRequest", back_populates="user", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )
    opportunities = relationship(
        "Opportunity", back_populates="user", foreign_keys="Opportunity.user_id"
    )


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class Profile(Base):
    """User profile with professional information.

    Extends the User entity with career-specific data. One-to-one with User.
    Serves as the single source of truth for resume pre-filling.
    """

    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Personal information (mandatory for profile completion)
    job_title = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    date_of_birth = Column(String(20), nullable=True)  # YYYY-MM-DD format

    # Links (optional)
    website = Column(String(512), nullable=True)
    linkedin = Column(String(512), nullable=True)
    github = Column(String(512), nullable=True)
    portfolio = Column(String(512), nullable=True)
    other_links = Column(Text, nullable=True)  # JSON array of {label, url}

    # Professional information
    summary = Column(Text, nullable=True)
    professional_headline = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    education_level = Column(String(100), nullable=True)

    # Resume sections stored as JSON (array of objects)
    education_json = Column(Text, nullable=True)  # [{degree, university, cgpa, graduation_year, field}]
    experience_json = Column(Text, nullable=True)  # [{company, role, duration, description, bullets}]
    projects_json = Column(Text, nullable=True)  # [{name, technologies, description, links}]
    skills_json = Column(Text, nullable=True)  # [{category, items}] or ["skill1", "skill2"]
    certifications_json = Column(Text, nullable=True)  # [{name, issuer, date}]
    achievements_json = Column(Text, nullable=True)  # [{title, description, date}]
    languages_json = Column(Text, nullable=True)  # [{language, proficiency}]
    interests_json = Column(Text, nullable=True)  # ["interest1", "interest2"]
    awards_json = Column(Text, nullable=True)  # [{name, issuer, date, description}]
    publications_json = Column(Text, nullable=True)  # [{title, publisher, date, url}]
    volunteer_json = Column(Text, nullable=True)  # [{organization, role, duration, description}]
    extracurricular_json = Column(Text, nullable=True)  # [{activity, description, duration}]

    # Profile completion tracking
    profile_completed = Column(Boolean, default=False, nullable=False)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)  # JSON string for SQLite compat

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")


# ---------------------------------------------------------------------------
# UserSession
# ---------------------------------------------------------------------------

class UserSession(Base):
    """Active user session tracking.

    Supports session management, revocation, and device association.
    Each session represents an authenticated state with a JWT token.
    """

    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device_id = Column(
        String(36),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Session data
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(Text, nullable=True)

    # Session lifecycle
    expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------

class Device(Base):
    """Registered user device.

    Tracks devices used to access the platform for security purposes.
    Supports trusted device management and device-specific sessions.
    """

    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Device information
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    os = Column(String(100), nullable=True)
    browser = Column(String(100), nullable=True)
    fingerprint = Column(String(255), nullable=True)  # Unique device fingerprint

    # Security
    is_trusted = Column(Boolean, default=False, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    user = relationship("User", back_populates="devices")
    sessions = relationship("UserSession", back_populates="device")


# ---------------------------------------------------------------------------
# LoginHistory
# ---------------------------------------------------------------------------

class LoginHistory(Base):
    """Login attempt audit log.

    Records every login attempt (success or failure) for security auditing
    and account recovery purposes. Immutable once created.
    """

    __tablename__ = "login_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    device_id = Column(
        String(36),
        ForeignKey("devices.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Login attempt data
    email_used = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    status = Column(
        String(20), nullable=False
    )  # success, failed, locked, oauth_callback
    failure_reason = Column(String(255), nullable=True)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="login_history")
    device = relationship("Device")


# ---------------------------------------------------------------------------
# OAuthAccount
# ---------------------------------------------------------------------------

class OAuthAccount(Base):
    """OAuth provider account linkage.

    Stores OAuth tokens and provider-specific user identifiers.
    Supports multiple OAuth providers per user (Google, GitHub, etc.).
    """

    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider information
    provider = Column(String(50), nullable=False, index=True)  # google, github, etc.
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255), nullable=True)
    provider_name = Column(String(255), nullable=True)
    provider_avatar_url = Column(String(512), nullable=True)

    # OAuth tokens
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scope = Column(Text, nullable=True)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

class Role(Base):
    """Role-based access control role.

    System roles (is_system=True) cannot be modified or deleted.
    Custom roles can be created by administrators.
    """

    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Role flags
    is_system = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    users = relationship("UserRole", back_populates="role")


# ---------------------------------------------------------------------------
# Permission
# ---------------------------------------------------------------------------

class Permission(Base):
    """Granular permission for RBAC.

    Permissions follow a resource:action pattern (e.g., resume:create).
    """

    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Permission structure
    resource = Column(String(100), nullable=True)  # e.g., "resume", "cover_letter"
    action = Column(String(50), nullable=True)  # e.g., "create", "read", "update", "delete"

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("RolePermission", back_populates="permission")


# ---------------------------------------------------------------------------
# UserRole (junction table)
# ---------------------------------------------------------------------------

class UserRole(Base):
    """User-Role assignment with expiry support.

    Supports temporary role assignments via expires_at.
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        String(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Assignment lifecycle
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="users")
    assigner = relationship("User", foreign_keys=[assigned_by])


# ---------------------------------------------------------------------------
# RolePermission (junction table)
# ---------------------------------------------------------------------------

class RolePermission(Base):
    """Role-Permission assignment."""

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(
        String(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id = Column(
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class Organization(Base):
    """Organization for team-based usage.

    Supports multi-tenant organization structure for enterprise features.
    """

    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(512), nullable=True)

    # Ownership
    owner_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# OrganizationMember (junction table)
# ---------------------------------------------------------------------------

class OrganizationMember(Base):
    """Organization membership."""

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id = Column(
        String(36),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )
    invited_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Membership lifecycle
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    inviter = relationship("User", foreign_keys=[invited_by])


# ---------------------------------------------------------------------------
# UserPreference
# ---------------------------------------------------------------------------

class UserPreference(Base):
    """Key-value user preferences.

    Supports arbitrary user settings organized by category.
    Values are stored as JSON strings for SQLite compatibility.
    """

    __tablename__ = "user_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "category", "key", name="uq_user_preference"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Preference structure
    category = Column(String(100), nullable=False)  # notifications, display, privacy, etc.
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)  # JSON string value

    # Metadata
    metadata_json = Column(String(2048), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")


# ---------------------------------------------------------------------------
# Subscription (preserved from original schema)
# ---------------------------------------------------------------------------

class Subscription(Base):
    """User subscription plan."""

    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_type = Column(String(50), nullable=False, default="free")
    status = Column(String(50), nullable=False, default="active")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")


# ---------------------------------------------------------------------------
# Payment (preserved from original schema)
# ---------------------------------------------------------------------------

class Payment(Base):
    """Payment transaction record."""

    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    subscription_id = Column(
        String(36), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    amount = Column(Integer, nullable=False)  # Changed from Numeric to Integer for SQLite compat
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="completed")
    payment_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
