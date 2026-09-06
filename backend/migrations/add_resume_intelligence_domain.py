"""Resume Intelligence Engine Migration Script.

This migration adds the Resume Intelligence Engine schema:
- Creates resume_profiles table
- Creates parsed_resume_data table
- Creates resume_entities table
- Creates resume_knowledge table

Usage:
    python -m migrations.add_resume_intelligence_domain

Or run the migrate() function directly from your application.
"""
import os
import sys
from datetime import datetime

from sqlalchemy import text

from .utils import (
    create_index_if_not_exists,
    create_table_if_not_exists,
    get_engine,
    table_exists,
)


def migrate() -> None:
    """Run the Resume Intelligence Engine migration."""
    print("Starting Resume Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()

    from app.models.resume_intelligence import (
        ParsedResumeData,
        ResumeEntity,
        ResumeKnowledge,
        ResumeProfile,
    )

    print("\n1. Creating new Resume Intelligence tables...")
    new_tables = [ResumeProfile, ParsedResumeData, ResumeEntity, ResumeKnowledge]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n2. Creating indexes...")
    indexes = [
        ("idx_rip_user_id", "resume_profiles", "user_id"),
        ("idx_rip_status", "resume_profiles", "status"),
        ("idx_prd_rip_id", "parsed_resume_data", "resume_profile_id"),
        ("idx_re_rip_id", "resume_entities", "resume_profile_id"),
        ("idx_re_type", "resume_entities", "entity_type"),
        ("idx_re_value", "resume_entities", "entity_value"),
        ("idx_rk_rip_id", "resume_knowledge", "resume_profile_id"),
    ]
    for idx_name, table_name, col_name in indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, col_name)

    print("\n" + "=" * 60)
    print("Resume Intelligence Engine migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")


def rollback() -> None:
    """Rollback the Resume Intelligence Engine migration."""
    print("Rolling back Resume Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = [
        "resume_knowledge",
        "resume_entities",
        "parsed_resume_data",
        "resume_profiles",
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
