"""Opportunity Intelligence Engine Migration Script.

This migration adds the Opportunity Intelligence Engine schema:
- Creates opportunities table
- Creates parsed_opportunity_data table
- Creates opportunity_entities table

Usage:
    python -m migrations.add_opportunity_domain

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
    """Run the Opportunity Intelligence Engine migration."""
    print("Starting Opportunity Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()

    # Import the ORM models we need
    from app.models.opportunity import Opportunity, OpportunityEntity, ParsedOpportunityData

    print("\n1. Creating new Opportunity tables...")
    new_tables = [Opportunity, ParsedOpportunityData, OpportunityEntity]
    for table in new_tables:
        create_table_if_not_exists(engine, table)

    print("\n2. Creating indexes...")
    indexes = [
        ("idx_opp_user_id", "opportunities", "user_id"),
        ("idx_opp_status", "opportunities", "status"),
        ("idx_pood_opp_id", "parsed_opportunity_data", "opportunity_id"),
        ("idx_oe_opp_id", "opportunity_entities", "opportunity_id"),
        ("idx_oe_type", "opportunity_entities", "entity_type"),
        ("idx_oe_value", "opportunity_entities", "entity_value"),
    ]
    for idx_name, table_name, col_name in indexes:
        if table_exists(engine, table_name):
            create_index_if_not_exists(engine, idx_name, table_name, col_name)

    print("\n" + "=" * 60)
    print("Opportunity Intelligence Engine migration completed successfully!")
    print("\nNew tables created:")
    for table in new_tables:
        print(f"  - {table.__tablename__}")


def rollback() -> None:
    """Rollback the Opportunity Intelligence Engine migration."""
    print("Rolling back Opportunity Intelligence Engine migration...")
    print("=" * 60)

    engine = get_engine()
    tables_to_drop = [
        "opportunity_entities",
        "parsed_opportunity_data",
        "opportunities",
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
