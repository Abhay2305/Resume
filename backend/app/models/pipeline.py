"""Pipeline Intelligence Engine domain models.

Tracks pipeline execution runs and individual stage execution within each run.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class PipelineRun(Base):
    """Pipeline execution run.

    Tracks a single end-to-end pipeline execution including all entity IDs
    produced by each stage, timing, and error information.
    """
    __tablename__ = "pipeline_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)
    # "pending" | "running" | "completed" | "failed"

    # Input
    resume_text = Column(Text, nullable=False)
    opportunity_text = Column(Text, nullable=False)

    # Output entity IDs (populated as stages complete)
    resume_profile_id = Column(String(36), nullable=True)
    opportunity_id = Column(String(36), nullable=True)
    gap_analysis_id = Column(String(36), nullable=True)
    knowledge_retrieval_id = Column(String(36), nullable=True)
    prompt_package_id = Column(String(36), nullable=True)
    ai_execution_id = Column(String(36), nullable=True)
    ai_validation_id = Column(String(36), nullable=True)

    # Metadata
    total_latency_ms = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    stages = relationship(
        "PipelineStage",
        back_populates="pipeline_run",
        order_by="PipelineStage.stage_order",
    )

    __table_args__ = (
        Index("ix_pipeline_runs_user_created", "user_id", "created_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class PipelineStage(Base):
    """Pipeline stage execution record.

    Tracks individual stage execution within a pipeline run including
    status, timing, entity ID produced, and error information.
    """
    __tablename__ = "pipeline_stages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_run_id = Column(
        String(36),
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stage identity
    stage_name = Column(String(50), nullable=False)
    stage_order = Column(Integer, nullable=False)

    # Status
    status = Column(String(20), nullable=False, default="pending")
    # "pending" | "running" | "completed" | "failed" | "skipped"

    # Result
    entity_id = Column(String(36), nullable=True)
    latency_ms = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationship
    pipeline_run = relationship("PipelineRun", back_populates="stages")

    __table_args__ = (
        Index("ix_pipeline_stages_run_order", "pipeline_run_id", "stage_order"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
