"""Gap Analysis domain models.

Compares structured Resume Knowledge against structured Opportunity Knowledge
and produces deterministic recommendations. No AI involved.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class GapAnalysisStatus(str):
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def values(cls):
        return [cls.PENDING, cls.ANALYZING, cls.COMPLETED, cls.FAILED]


class GapAnalysis(Base):
    """Gap Analysis record.

    Represents a comparison between Resume Knowledge and Opportunity Knowledge.
    """
    __tablename__ = "gap_analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_profile_id = Column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    opportunity_id = Column(
        String(36),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(20), nullable=False, default=GapAnalysisStatus.PENDING)
    overall_match_score = Column(Float, nullable=True)
    skill_match_score = Column(Float, nullable=True)
    technology_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    education_match_score = Column(Float, nullable=True)
    certification_match_score = Column(Float, nullable=True)
    keyword_match_score = Column(Float, nullable=True)
    total_gaps = Column(Integer, nullable=True, default=0)
    total_matches = Column(Integer, nullable=True, default=0)
    total_recommendations = Column(Integer, nullable=True, default=0)
    parser_version = Column(String(50), nullable=True, default="1.0")
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    resume_profile = relationship("ResumeProfile", foreign_keys=[resume_profile_id])
    opportunity = relationship("Opportunity", foreign_keys=[opportunity_id])
    gap_results = relationship("GapResult", back_populates="gap_analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="gap_analysis", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("user_id", "resume_profile_id", "opportunity_id", name="uq_gap_analysis_user_resume_opportunity"),
        Index("ix_gap_analysis_status", "status"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class GapResult(Base):
    """Individual gap comparison result.

    Stores the result of comparing a specific category between resume and opportunity.
    """
    __tablename__ = "gap_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True)
    match_score = Column(Float, nullable=True)
    matched_items = Column(Text, nullable=True)
    missing_items = Column(Text, nullable=True)
    partial_items = Column(Text, nullable=True)
    extra_items = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    gap_analysis = relationship("GapAnalysis", back_populates="gap_results")

    __table_args__ = (
        UniqueConstraint("gap_analysis_id", "category", name="uq_gap_result_analysis_category"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class Recommendation(Base):
    """Deterministic recommendation based on gap analysis.

    Generated without AI. Each recommendation has a clear action and priority.
    """
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), nullable=False, default="medium")
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    target_item = Column(String(255), nullable=True)
    is_applied = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    gap_analysis = relationship("GapAnalysis", back_populates="recommendations")

    __table_args__ = (
        Index("ix_recommendations_priority", "priority"),
        Index("ix_recommendations_action", "action"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
