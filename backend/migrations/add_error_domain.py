"""Error Domain Migration Script.

This migration adds the complete Error domain schema:
- Creates error_logs table for immutable error entries
- Creates error_categories table for categorization
- Creates error_resolutions table for resolution workflow
- Creates error_occurrences table for frequency tracking
- Creates error_archive table for long-term storage

Usage:
    python -m migrations.add_error_domain

Or run the migrate() function directly from your application.
"""
import os
import sys

from sqlalchemy import text

from .utils import (
    create_index_if_not_exists,
    create_table_if_not_exists,
    get_engine,
    table_exists,
)


def migrate() -> None:
    """Run the Error domain migration."""
    print("Starting Error Domain migration...")
    print("=" * 60)

    engine = get_engine()

    from app.models.error import (
        ErrorArchive,
        ErrorCategory,
        ErrorLog,
        ErrorOccurrence,
        ErrorResolution,
    )

    print("\n1. Creating Error tables...")
    new_tables = [ErrorCategory, ErrorResolution, ErrorLog, ErrorOccurrence, ErrorArchive]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n2. Creating indexes...")
    indexes = [
        ("idx_error_user", "error_logs", "user_id"),
        ("idx_error_session", "error_logs", "session_id"),
        ("idx_error_request", "error_logs", "request_id"),
        ("idx_error_correlation", "error_logs", "correlation_id"),
        ("idx_error_type", "error_logs", "error_type"),
        ("idx_error_fingerprint", "error_logs", "error_fingerprint"),
        ("idx_error_severity", "error_logs", "severity"),
        ("idx_error_status", "error_logs", "status"),
        ("idx_error_environment", "error_logs", "environment"),
        ("idx_error_created", "error_logs", "created_at"),
        ("idx_error_resolution", "error_logs", "resolution_id"),
        ("idx_error_category", "error_logs", "category_id"),
        ("idx_error_resume", "error_logs", "resume_id"),
        ("idx_error_cover_letter", "error_logs", "cover_letter_id"),
        ("idx_error_organization", "error_logs", "organization_id"),
        ("idx_error_user_status", "error_logs", "user_id, status"),
        ("idx_error_severity_created", "error_logs", "severity, created_at"),
        ("idx_error_fingerprint_status", "error_logs", "error_fingerprint, status"),
        ("idx_error_environment_severity", "error_logs", "environment, severity"),
        ("idx_error_category_name", "error_categories", "name"),
        ("idx_error_occurrence_log", "error_occurrences", "error_log_id"),
        ("idx_error_occurrence_fingerprint", "error_occurrences", "error_fingerprint"),
        ("idx_error_occurrence_created", "error_occurrences", "created_at"),
        ("idx_error_archive_original", "error_archive", "original_id"),
        ("idx_error_archive_created", "error_archive", "created_at"),
        ("idx_error_archive_fingerprint", "error_archive", "error_fingerprint"),
        ("idx_error_resolution_type", "error_resolutions", "resolution_type"),
        ("idx_error_resolution_assigned", "error_resolutions", "assigned_to"),
    ]
    for idx_name, table_name, col_name in indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, col_name)

    print("\n" + "=" * 60)
    print("Error Domain migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")
    print("\nRun 'python -m app.seed' to seed default error categories.")


def rollback() -> None:
    """Rollback the Error domain migration."""
    print("Rolling back Error Domain migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = [
        "error_archive", "error_occurrences", "error_logs",
        "error_resolutions", "error_categories",
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
