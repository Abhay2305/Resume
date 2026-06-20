"""Reusable SQLAlchemy mixins.

These encode the long-term, future-proof column conventions required of every
new table in the platform data model:

- ``UUIDPrimaryKeyMixin``  -> string UUID primary key
- ``TimestampMixin``       -> created_at / updated_at
- ``MetadataMixin``        -> metadata_json (free-form, additive evolution)
- ``SoftDeleteMixin``      -> deleted_at (nullable; soft delete support)

Mixins are composed per table so each table only carries what it needs, while
guaranteeing consistency without duplicating column definitions.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON


def generate_uuid() -> str:
    """Return a new random UUID4 as a string (used for all primary keys)."""
    return str(uuid.uuid4())


class UUIDPrimaryKeyMixin:
    """String UUID primary key, consistent with the existing schema."""

    id = Column(String(36), primary_key=True, default=generate_uuid)


class TimestampMixin:
    """created_at / updated_at timestamps maintained automatically."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class MetadataMixin:
    """Free-form JSON metadata column.

    Allows additive evolution of a table without a migration for every new
    optional attribute. Stored as ``metadata_json`` to avoid clashing with
    SQLAlchemy's reserved ``metadata`` attribute on declarative classes.
    """

    metadata_json = Column(JSON, nullable=True, default=dict)


class SoftDeleteMixin:
    """Soft-delete support via a nullable ``deleted_at`` timestamp.

    Rows are never physically removed by application code that respects this
    mixin; instead ``deleted_at`` is set. Repositories filter it out by default.
    """

    deleted_at = Column(DateTime, nullable=True, default=None)
