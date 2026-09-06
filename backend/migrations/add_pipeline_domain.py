"""Pipeline Intelligence Engine Migration Script.

This migration adds the Pipeline Intelligence Engine schema:
- Creates pipeline_runs table for pipeline execution tracking
- Creates pipeline_stages table for individual stage execution

Usage:
    python -m migrations.add_pipeline_domain

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
    """Run the Pipeline Intelligence Engine migration."""
    print("Starting Pipeline Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()

    from app.models.pipeline import PipelineRun, PipelineStage

    print("\n1. Creating Pipeline tables...")
    new_tables = [PipelineRun, PipelineStage]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n2. Creating indexes...")
    # Composite indexes (column-level indexes are created by SQLAlchemy)
    composite_indexes = [
        ("ix_pipeline_runs_user_created", "pipeline_runs", "user_id, created_at"),
        ("ix_pipeline_stages_run_order", "pipeline_stages", "pipeline_run_id, stage_order"),
    ]
    for idx_name, table_name, cols in composite_indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, cols)

    print("\n" + "=" * 60)
    print("Pipeline Intelligence Engine migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")


def rollback() -> None:
    """Rollback the Pipeline Intelligence Engine migration."""
    print("Rolling back Pipeline Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = [
        "pipeline_stages",
        "pipeline_runs",
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
