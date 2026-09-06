"""Shared migration utilities for PostgreSQL and SQLite.

Provides database-agnostic helpers for schema migrations.
PostgreSQL is the primary target; SQLite is supported for testing.
"""
import os
import sys
from typing import Optional

from sqlalchemy import Column, create_engine, inspect, text
from sqlalchemy.engine import Engine

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_engine(database_url: Optional[str] = None) -> Engine:
    """Get database engine from environment or parameter.

    PostgreSQL is the primary database. Falls back to SQLite only when
    DATABASE_URL explicitly starts with 'sqlite'.
    """
    if database_url is None:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/resume_builder",
        )

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    connect_args = {}
    pool_settings = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        pool_settings = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }

    return create_engine(database_url, connect_args=connect_args, **pool_settings)


def table_exists(engine: Engine, table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def column_exists(engine: Engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    if not table_exists(engine, table_name):
        return False
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def index_exists(engine: Engine, table_name: str, index_name: str) -> bool:
    """Check if an index exists."""
    if not table_exists(engine, table_name):
        return False
    inspector = inspect(engine)
    indexes = inspector.get_indexes(table_name)
    return any(idx["name"] == index_name for idx in indexes)


def add_column(engine: Engine, table_name: str, column: Column) -> None:
    """Add a column to an existing table. Works on both PostgreSQL and SQLite."""
    if column_exists(engine, table_name, column.name):
        print(f"  Column {table_name}.{column.name} already exists, skipping")
        return

    dialect = engine.dialect.name
    col_type = column.type.compile(engine.dialect)

    if dialect == "sqlite":
        # SQLite has limited ALTER TABLE support
        col_str = f"{column.name} {col_type}"
        if column.default is not None and hasattr(column.default, "arg"):
            default_val = column.default.arg
            if isinstance(default_val, bool):
                col_str += f" DEFAULT {1 if default_val else 0}"
            elif isinstance(default_val, str):
                col_str += f" DEFAULT '{default_val}'"
            elif default_val is not None:
                col_str += f" DEFAULT {default_val}"
        elif not column.nullable:
            col_str += " DEFAULT ''"
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_str}"))
            conn.commit()
    else:
        # PostgreSQL
        nullable = "NULL" if column.nullable else "NOT NULL"
        default = ""
        if column.default is not None and hasattr(column.default, "arg"):
            default_val = column.default.arg
            if isinstance(default_val, bool):
                default = f" DEFAULT {default_val}"
            elif isinstance(default_val, str):
                default = f" DEFAULT '{default_val}'"
            elif default_val is not None:
                default = f" DEFAULT {default_val}"
        with engine.connect() as conn:
            conn.execute(
                text(
                    f"ALTER TABLE {table_name} ADD COLUMN "
                    f"{column.name} {col_type} {nullable}{default}"
                )
            )
            conn.commit()

    print(f"  Added column {table_name}.{column.name}")


def create_table_if_not_exists(engine: Engine, table_class) -> None:
    """Create a table from ORM class if it doesn't exist."""
    if not table_exists(engine, table_class.__tablename__):
        table_class.__table__.create(bind=engine)
        print(f"  Created table {table_class.__tablename__}")
    else:
        print(f"  Table {table_class.__tablename__} already exists, skipping")


def create_index_if_not_exists(
    engine: Engine, index_name: str, table_name: str, columns: str
) -> None:
    """Create an index if it doesn't exist."""
    if index_exists(engine, table_name, index_name):
        print(f"  Index {index_name} already exists, skipping")
        return
    with engine.connect() as conn:
        conn.execute(text(f"CREATE INDEX {index_name} ON {table_name} ({columns})"))
        conn.commit()
    print(f"  Created index {index_name}")
