"""Error domain models.

Provides comprehensive error logging, categorization, and resolution tracking.
Designed as a reusable platform component that every module can use.

Design Principles:
- Immutable error logs (no updates, no deletes)
- High-performance writes via async-compatible patterns
- Error fingerprinting for deduplication
- Resolution workflow support
- Retry tracking for transient errors
- Environment-aware logging
- Correlation IDs for distributed tracing
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
from sqlalchemy.orm import relationship

from .base import Base


# ---------------------------------------------------------------------------
# ErrorCategory
# ---------------------------------------------------------------------------

class ErrorCategory(Base):
    """Categorization for errors.

    Helps organize errors by type for reporting and resolution workflows.
    """

    __tablename__ = "error_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color for UI
    icon = Column(String(50), nullable=True)  # Icon identifier

    # Auto-categorization rules (JSON string of patterns)
    patterns = Column(Text, nullable=True)  # JSON array of regex patterns

    # Severity mapping
    default_severity = Column(String(20), nullable=False, default="medium")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    errors = relationship("ErrorLog", back_populates="category")


# ---------------------------------------------------------------------------
# ErrorResolution
# ---------------------------------------------------------------------------

class ErrorResolution(Base):
    """Resolution workflow for errors.

    Tracks how errors are resolved for learning and prevention.
    """

    __tablename__ = "error_resolutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Resolution details
    resolution_type = Column(
        String(50), nullable=False
    )  # fixed, wont_fix, duplicate, external, by_design
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Assignment
    assigned_to = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Resolution metadata
    root_cause = Column(Text, nullable=True)
    fix_commit = Column(String(255), nullable=True)  # Git commit hash
    fix_pr = Column(String(255), nullable=True)  # PR URL

    # Prevention
    prevention_notes = Column(Text, nullable=True)
    test_added = Column(Boolean, default=False, nullable=False)

    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to])
    verifier = relationship("User", foreign_keys=[verified_by])
    errors = relationship("ErrorLog", back_populates="resolution")


# ---------------------------------------------------------------------------
# ErrorLog
# ---------------------------------------------------------------------------

class ErrorLog(Base):
    """Primary error logging entity.

    Captures every error with full context for debugging and analysis.
    Designed for high-throughput writes with minimal locking.
    """

    __tablename__ = "error_logs"

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

    # Error identification
    error_type = Column(String(255), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    error_fingerprint = Column(String(64), nullable=False, index=True)  # SHA-256 for dedup

    # Source location
    module = Column(String(255), nullable=True)
    function = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    router = Column(String(100), nullable=True, index=True)  # Router prefix, e.g. "procs", "errors"

    # Stack trace
    stack_trace = Column(Text, nullable=True)

    # Request context
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    request_payload = Column(Text, nullable=True)  # JSON, sensitive data redacted
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    browser = Column(String(100), nullable=True)

    # Response context
    response_status = Column(Integer, nullable=True)

    # Performance
    processing_time_ms = Column(Integer, nullable=True)

    # Severity and environment
    severity = Column(
        String(20), nullable=False, default="medium", index=True
    )  # low, medium, high, critical
    environment = Column(
        String(50), nullable=False, index=True
    )  # development, staging, production
    python_version = Column(String(20), nullable=True)
    database_provider = Column(String(50), nullable=True)
    ai_provider = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)

    # Retry tracking
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)

    # Resolution status
    status = Column(
        String(50), nullable=False, default="new", index=True
    )  # new, acknowledged, investigating, resolved, wont_fix
    resolution_id = Column(
        String(36),
        ForeignKey("error_resolutions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Category
    category_id = Column(
        String(36),
        ForeignKey("error_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Domain-specific references (nullable for future use)
    resume_id = Column(String(36), nullable=True, index=True)
    cover_letter_id = Column(String(36), nullable=True, index=True)
    organization_id = Column(String(36), nullable=True, index=True)
    device_id = Column(String(36), nullable=True)

    # Occurrence tracking
    first_occurrence_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_occurrence_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    occurrence_count = Column(Integer, default=1, nullable=False)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamp (immutable)
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        Index("idx_error_user_status", "user_id", "status"),
        Index("idx_error_severity_created", "severity", "created_at"),
        Index("idx_error_fingerprint_status", "error_fingerprint", "status"),
        Index("idx_error_environment", "environment", "severity"),
    )

    # Relationships
    category = relationship("ErrorCategory", back_populates="errors")
    resolution = relationship("ErrorResolution", back_populates="errors")


# ---------------------------------------------------------------------------
# ErrorOccurrence
# ---------------------------------------------------------------------------

class ErrorOccurrence(Base):
    """Individual error occurrences for tracking frequency.

    When the same error happens multiple times, each occurrence is logged
    separately while linking to the parent ErrorLog via fingerprint.
    """

    __tablename__ = "error_occurrences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    error_log_id = Column(
        String(36),
        ForeignKey("error_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    error_fingerprint = Column(String(64), nullable=False, index=True)

    # Occurrence context
    user_id = Column(String(36), nullable=True)
    session_id = Column(String(36), nullable=True)
    request_id = Column(String(36), nullable=True)
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Occurrence-specific data
    request_payload = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Retry context
    is_retry = Column(Boolean, default=False, nullable=False)
    retry_attempt = Column(Integer, default=0, nullable=False)

    # Metadata
    metadata_json = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    error_log = relationship("ErrorLog")


# ---------------------------------------------------------------------------
# ErrorArchive
# ---------------------------------------------------------------------------

class ErrorArchive(Base):
    """Archived error logs for long-term storage.

    Same schema as ErrorLog but stored separately for performance.
    Used for historical analysis and compliance.
    """

    __tablename__ = "error_archive"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_id = Column(String(36), nullable=False, index=True)

    # All fields same as ErrorLog
    user_id = Column(String(36), nullable=True, index=True)
    session_id = Column(String(36), nullable=True)
    request_id = Column(String(36), nullable=True)
    correlation_id = Column(String(36), nullable=True)
    error_type = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=False)
    error_fingerprint = Column(String(64), nullable=False)
    module = Column(String(255), nullable=True)
    function = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    line_number = Column(Integer, nullable=True)
    stack_trace = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    request_payload = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    browser = Column(String(100), nullable=True)
    response_status = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    severity = Column(String(20), nullable=False)
    environment = Column(String(50), nullable=False)
    python_version = Column(String(20), nullable=True)
    database_provider = Column(String(50), nullable=True)
    ai_provider = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), nullable=False)
    resolution_id = Column(String(36), nullable=True)
    category_id = Column(String(36), nullable=True)
    resume_id = Column(String(36), nullable=True)
    cover_letter_id = Column(String(36), nullable=True)
    organization_id = Column(String(36), nullable=True)
    device_id = Column(String(36), nullable=True)
    first_occurrence_at = Column(DateTime, nullable=False)
    last_occurrence_at = Column(DateTime, nullable=False)
    occurrence_count = Column(Integer, default=1, nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)

    # Archive metadata
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False)
