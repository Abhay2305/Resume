"""Shared declarative base for all ORM models.

Every domain module imports ``Base`` from here so that a single
``Base.metadata`` describes the whole schema (used by ``create_all`` and by
Alembic autogenerate).
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
