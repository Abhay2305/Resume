"""Identity Domain Migration Script.

This migration adds the complete Identity domain schema:
- Enhances users table with new security fields
- Creates sessions, devices, login_history, oauth_accounts tables
- Creates roles, permissions, user_roles, role_permissions tables
- Creates organizations, organization_members tables
- Creates user_preferences table

Usage:
    python -m migrations.add_identity_domain

Or run the migrate() function directly from your application.
"""
import os
import sys
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    text,
)

from .utils import (
    add_column,
    create_index_if_not_exists,
    create_table_if_not_exists,
    get_engine,
    table_exists,
)


def migrate() -> None:
    """Run the Identity domain migration."""
    print("Starting Identity Domain migration...")
    print("=" * 60)

    engine = get_engine()

    # Import the ORM models we need
    from app.models.base import Base
    from app.models.identity import (
        Device,
        LoginHistory,
        OAuthAccount,
        Organization,
        OrganizationMember,
        Permission,
        Profile,
        Role,
        RolePermission,
        User,
        UserPreference,
        UserRole,
        UserSession,
    )

    print("\n1. Enhancing users table...")
    add_column(engine, "users", Column("is_active", Boolean, default=True, nullable=False))
    add_column(engine, "users", Column("is_verified", Boolean, default=False, nullable=False))
    add_column(engine, "users", Column("is_superuser", Boolean, default=False, nullable=False))
    add_column(engine, "users", Column("avatar_url", String(512), nullable=True))
    add_column(engine, "users", Column("timezone", String(50), nullable=True))
    add_column(engine, "users", Column("language", String(10), default="en", nullable=False))
    add_column(engine, "users", Column("last_login_at", DateTime, nullable=True))
    add_column(engine, "users", Column("last_login_ip", String(45), nullable=True))
    add_column(engine, "users", Column("failed_login_attempts", Integer, default=0, nullable=False))
    add_column(engine, "users", Column("locked_until", DateTime, nullable=True))
    add_column(engine, "users", Column("password_changed_at", DateTime, nullable=True))
    add_column(engine, "users", Column("metadata_json", String(2048), nullable=True))
    add_column(engine, "users", Column("deleted_at", DateTime, nullable=True))

    print("\n2. Enhancing profiles table...")
    add_column(engine, "profiles", Column("company", String(255), nullable=True))
    add_column(engine, "profiles", Column("industry", String(100), nullable=True))
    add_column(engine, "profiles", Column("years_of_experience", Integer, nullable=True))
    add_column(engine, "profiles", Column("education_level", String(100), nullable=True))
    add_column(engine, "profiles", Column("metadata_json", String(2048), nullable=True))

    print("\n3. Creating new Identity tables...")
    new_tables = [
        UserSession, Device, LoginHistory, OAuthAccount,
        Role, Permission, UserRole, RolePermission,
        Organization, OrganizationMember, UserPreference,
    ]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n4. Creating indexes...")
    indexes = [
        ("idx_user_sessions_token", "user_sessions", "token_hash"),
        ("idx_user_sessions_user", "user_sessions", "user_id"),
        ("idx_devices_user", "devices", "user_id"),
        ("idx_devices_fingerprint", "devices", "fingerprint"),
        ("idx_login_history_user", "login_history", "user_id"),
        ("idx_login_history_email", "login_history", "email_used"),
        ("idx_oauth_accounts_user", "oauth_accounts", "user_id"),
        ("idx_oauth_accounts_provider", "oauth_accounts", "provider"),
        ("idx_user_roles_user", "user_roles", "user_id"),
        ("idx_user_roles_role", "user_roles", "role_id"),
        ("idx_role_permissions_role", "role_permissions", "role_id"),
        ("idx_role_permissions_permission", "role_permissions", "permission_id"),
        ("idx_organizations_slug", "organizations", "slug"),
        ("idx_organizations_owner", "organizations", "owner_id"),
        ("idx_org_members_org", "organization_members", "organization_id"),
        ("idx_org_members_user", "organization_members", "user_id"),
        ("idx_user_preferences_user", "user_preferences", "user_id"),
    ]
    for idx_name, table_name, col_name in indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, col_name)

    print("\n" + "=" * 60)
    print("Identity Domain migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")
    print("\nRun 'python -m app.seed' to seed default roles and permissions.")


def rollback() -> None:
    """Rollback the Identity domain migration."""
    print("Rolling back Identity Domain migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = [
        "user_preferences", "organization_members", "organizations",
        "role_permissions", "user_roles", "login_history",
        "oauth_accounts", "devices", "user_sessions",
        "permissions", "roles",
    ]

    with engine.connect() as conn:
        for table_name in tables_to_drop:
            if table_exists(engine, table_name):
                try:
                    conn.execute(text(f"DROP TABLE {table_name} CASCADE"))
                    print(f"  Dropped table {table_name}")
                except Exception as e:
                    print(f"  Warning: Could not drop {table_name}: {e}")
            else:
                print(f"  Table {table_name} does not exist, skipping")
        conn.commit()

    print("\n" + "=" * 60)
    print("Rollback completed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
