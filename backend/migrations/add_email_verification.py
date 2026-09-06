"""Add email verification columns to users table.

These columns were added to the User model in identity.py but
never migrated to the database. This migration adds them.

Usage:
    python -m migrations.add_email_verification
"""
import os
import sys

from sqlalchemy import Column, DateTime, String

from .utils import add_column, get_engine


def migrate() -> None:
    """Add email verification columns to users table."""
    print("Adding email verification columns to users table...")
    print("=" * 60)

    engine = get_engine()

    add_column(engine, "users", Column("email_verified_at", DateTime, nullable=True))
    add_column(engine, "users", Column("verification_token", String(255), nullable=True, index=True))
    add_column(engine, "users", Column("verification_token_expires_at", DateTime, nullable=True))

    print("=" * 60)
    print("Email verification migration complete.")


if __name__ == "__main__":
    migrate()
