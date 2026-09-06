"""Migration: Add router column to error_logs.

Usage:
    python -m migrations.add_error_router
"""
import os
import sys

from sqlalchemy import Column, String

from .utils import add_column, create_index_if_not_exists, get_engine


def migrate() -> None:
    """Add router column to error_logs."""
    print("Adding router column to error_logs...")
    print("=" * 60)

    engine = get_engine()

    router_col = Column("router", String(100), nullable=True)
    add_column(engine, "error_logs", router_col)

    print("\nCreating index ix_error_logs_router...")
    create_index_if_not_exists(
        engine, "ix_error_logs_router", "error_logs", "router"
    )

    print("\nDone!")


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    migrate()
