"""Audit domain models.

Provides comprehensive audit logging for all backend actions. Designed to be
reusable across every future domain with minimal configuration.

Design Principles:
- Immutable audit logs (no updates, no deletes)
- High-performance writes via async-compatible patterns
- Partitioned by date for efficient archival and cleanup
- JSON fields for flexible state storage
- Correlation IDs for distributed tracing
- Configurable retention policies per entity type
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from .base import Base


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

class AuditLog(Base):
    """Immutable audit log entry.

    Captures every significant action in the system. Records before/after
    state for full change tracking. Designed for high-throughput writes
    with minimal locking.
    """

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity context
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    session_id = Column(String(36), nullable=True, index=True)

    # Correlation / tracing
    request_id = Column(String(36), nullable=True, index=True)
    correlation_id = Column(String(36), nullable=True, index=True)

    # Entity reference (what was acted upon)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(36), nullable=True, index=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # State tracking (JSON strings for SQLite compatibility)
    previous_state = Column(Text, nullable=True)  # JSON
    new_state = Column(Text, nullable=True)  # JSON

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    request_body = Column(Text, nullable=True)  # JSON, sensitive data redacted

    # Response context
    response_status = Column(Integer, nullable=True)
    response_body_summary = Column(Text, nullable=True)  # Truncated response
    error_message = Column(Text, nullable=True)

    # Performance
    processing_time_ms = Column(Integer, nullable=True)

    # Metadata
    metadata_json = Column(Text, nullable=True)  # JSON for extensibility
    tags = Column(String(500), nullable=True)  # Comma-separated tags

    # Timestamp (immutable)
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_created", "created_at"),
    )


# ---------------------------------------------------------------------------
# AuditConfig
# ---------------------------------------------------------------------------

class AuditConfig(Base):
    """Configuration for audit logging behavior.

    Controls which entities are audited, retention periods, and
    sensitive field redaction rules.
    """

    __tablename__ = "audit_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Entity configuration
    entity_type = Column(String(100), unique=True, nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # What to audit
    audit_create = Column(Boolean, default=True, nullable=False)
    audit_read = Column(Boolean, default=False, nullable=False)  # Usually too verbose
    audit_update = Column(Boolean, default=True, nullable=False)
    audit_delete = Column(Boolean, default=True, nullable=False)

    # Retention
    retention_days = Column(Integer, default=365, nullable=False)
    archive_after_days = Column(Integer, default=90, nullable=False)

    # Redaction rules (JSON string of field names to redact)
    sensitive_fields = Column(Text, nullable=True)  # JSON array

    # Sampling (for high-volume reads)
    sample_rate = Column(Integer, default=100, nullable=False)  # Percentage (1-100)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ---------------------------------------------------------------------------
# AuditArchive
# ---------------------------------------------------------------------------

class AuditArchive(Base):
    """Archived audit logs for long-term storage.

    Same schema as AuditLog but stored separately for performance.
    Used for compliance and historical analysis.
    """

    __tablename__ = "audit_archive"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # All fields same as AuditLog
    user_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(36), nullable=True)
    request_id = Column(String(36), nullable=True)
    correlation_id = Column(String(36), nullable=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(36), nullable=True)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_body_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, index=True)

    # Archive metadata
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    original_id = Column(String(36), nullable=False, index=True)


# ---------------------------------------------------------------------------
# AuditExport
# ---------------------------------------------------------------------------

class AuditExport(Base):
    """Tracks audit log export jobs for compliance."""

    __tablename__ = "audit_exports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Export criteria
    requested_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    entity_type = Column(String(100), nullable=True)  # NULL = all entities
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    filters_json = Column(Text, nullable=True)  # JSON filters

    # Export status
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
