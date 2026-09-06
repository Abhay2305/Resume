"""Audit Domain Migration Script.

This migration adds the complete Audit domain schema:
- Creates audit_logs table for immutable audit entries
- Creates audit_configs table for per-entity configuration
- Creates audit_archive table for long-term storage
- Creates audit_exports table for compliance exports

Usage:
    python -m migrations.add_audit_domain

Or run the migrate() function directly from your application.
"""
import os
import sys

from sqlalchemy import text

from .utils import (
    create_index_if_not_exists,
    create_table_if_not_exists,
    get_engine,
    index_exists,
    table_exists,
)


def migrate() -> None:
    """Run the Audit domain migration."""
    print("Starting Audit Domain migration...")
    print("=" * 60)

    engine = get_engine()

    from app.models.audit import AuditArchive, AuditConfig, AuditExport, AuditLog

    print("\n1. Creating Audit tables...")
    new_tables = [AuditLog, AuditConfig, AuditArchive, AuditExport]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n2. Creating indexes...")
    # Single-column indexes
    indexes = [
        ("idx_audit_user", "audit_logs", "user_id"),
        ("idx_audit_session", "audit_logs", "session_id"),
        ("idx_audit_request", "audit_logs", "request_id"),
        ("idx_audit_correlation", "audit_logs", "correlation_id"),
        ("idx_audit_entity_type", "audit_logs", "entity_type"),
        ("idx_audit_entity_id", "audit_logs", "entity_id"),
        ("idx_audit_action", "audit_logs", "action"),
        ("idx_audit_created", "audit_logs", "created_at"),
        ("idx_audit_config_entity", "audit_configs", "entity_type"),
        ("idx_audit_archive_original", "audit_archive", "original_id"),
        ("idx_audit_archive_created", "audit_archive", "created_at"),
        ("idx_audit_archive_entity_type", "audit_archive", "entity_type"),
        ("idx_audit_archive_entity_id", "audit_archive", "entity_id"),
        ("idx_audit_export_requested_by", "audit_exports", "requested_by"),
    ]
    for idx_name, table_name, col_name in indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, col_name)

    # Composite indexes
    composite_indexes = [
        ("idx_audit_entity", "audit_logs", "entity_type, entity_id"),
        ("idx_audit_user_action", "audit_logs", "user_id, action"),
    ]
    for idx_name, table_name, cols in composite_indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, cols)

    print("\n" + "=" * 60)
    print("Audit Domain migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")
    print("\nRun 'python -m app.seed' to seed default audit configurations.")


def rollback() -> None:
    """Rollback the Audit domain migration."""
    print("Rolling back Audit Domain migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = ["audit_exports", "audit_archive", "audit_configs", "audit_logs"]

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
