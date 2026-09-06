"""AI Response Intelligence Engine domain models.

Validates, analyzes, explains, and compares every AI response before it
can become part of a resume. The security layer between AI and the database.
"""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    REJECTED = "rejected"
    FAILED = "failed"


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"


class ChangeCategory(str, Enum):
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    SKILLS = "skills"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    KEYWORDS = "keywords"
    FORMATTING = "formatting"
    ACHIEVEMENTS = "achievements"
    CONTACT = "contact"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIResponseValidation(Base):
    """Main validation record for an AI response.

    Links an AI execution to its full validation pipeline result.
    """
    __tablename__ = "ai_response_validations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_execution_id = Column(
        String(36),
        ForeignKey("ai_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prompt_package_id = Column(
        String(36),
        ForeignKey("prompt_packages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_profile_id = Column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status = Column(String(20), nullable=False, default=ValidationStatus.PENDING.value, index=True)
    is_approved = Column(Boolean, nullable=True, default=None)
    schema_valid = Column(Boolean, nullable=True, default=None)
    truth_valid = Column(Boolean, nullable=True, default=None)
    knowledge_valid = Column(Boolean, nullable=True, default=None)
    gap_valid = Column(Boolean, nullable=True, default=None)
    overall_confidence = Column(Float, nullable=True)
    total_changes = Column(Integer, nullable=True, default=0)
    approved_changes = Column(Integer, nullable=True, default=0)
    rejected_changes = Column(Integer, nullable=True, default=0)
    warning_count = Column(Integer, nullable=True, default=0)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    ai_execution = relationship("AIExecution", foreign_keys=[ai_execution_id])
    prompt_package = relationship("PromptPackage", foreign_keys=[prompt_package_id])
    resume_profile = relationship("ResumeProfile", foreign_keys=[resume_profile_id])
    gap_analysis = relationship("GapAnalysis", foreign_keys=[gap_analysis_id])
    diffs = relationship("ResumeDiff", back_populates="validation", cascade="all, delete-orphan")
    change_sets = relationship("ChangeSet", back_populates="validation", cascade="all, delete-orphan")
    validation_reports = relationship("ValidationReport", back_populates="validation", cascade="all, delete-orphan")
    confidence_scores = relationship("ConfidenceScore", back_populates="validation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_ai_response_validations_user_created", "user_id", "created_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class ResumeDiff(Base):
    """Deterministic diff between original resume and AI response.

    Stores added, removed, modified, and moved items.
    Never overwrites the resume.
    """
    __tablename__ = "resume_diffs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    validation_id = Column(
        String(36),
        ForeignKey("ai_response_validations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section = Column(String(50), nullable=False, index=True)
    change_type = Column(String(20), nullable=False, index=True)
    original_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    field_path = Column(String(255), nullable=True)
    item_index = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    validation = relationship("AIResponseValidation", back_populates="diffs")

    __table_args__ = (
        Index("ix_resume_diffs_section_type", "section", "change_type"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class ChangeSet(Base):
    """Categorized change set for frontend rendering.

    Every change is classified by category and type.
    """
    __tablename__ = "change_sets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    validation_id = Column(
        String(36),
        ForeignKey("ai_response_validations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True)
    change_type = Column(String(20), nullable=False, index=True)
    description = Column(Text, nullable=False)
    original_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    is_approved = Column(Boolean, nullable=True, default=None)
    risk_level = Column(String(20), nullable=True)
    supporting_rule_id = Column(String(36), nullable=True)
    supporting_gap_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    validation = relationship("AIResponseValidation", back_populates="change_sets")

    __table_args__ = (
        Index("ix_change_sets_category_type", "category", "change_type"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class ValidationReport(Base):
    """Detailed validation report.

    Stores the full validation result for each validator.
    """
    __tablename__ = "validation_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    validation_id = Column(
        String(36),
        ForeignKey("ai_response_validations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    validator_name = Column(String(100), nullable=False, index=True)
    is_valid = Column(Boolean, nullable=False, default=False)
    score = Column(Float, nullable=True)
    issues = Column(JSON, nullable=True)
    details = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    validation = relationship("AIResponseValidation", back_populates="validation_reports")

    __table_args__ = (
        UniqueConstraint("validation_id", "validator_name", name="uq_validation_report"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class ConfidenceScore(Base):
    """Confidence score for individual changes.

    Every change receives a confidence score with supporting evidence.
    """
    __tablename__ = "confidence_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    validation_id = Column(
        String(36),
        ForeignKey("ai_response_validations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    change_set_id = Column(
        String(36),
        ForeignKey("change_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    supporting_gap_id = Column(String(36), nullable=True)
    supporting_rule_id = Column(String(36), nullable=True)
    validation_result = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    validation = relationship("AIResponseValidation", back_populates="confidence_scores")
    change_set = relationship("ChangeSet", foreign_keys=[change_set_id])

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
