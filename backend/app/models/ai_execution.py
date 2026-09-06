"""AI Execution Engine domain models.

Tracks AI execution requests, responses, and metadata.
Does NOT store AI-generated resume content - only execution metadata.
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


class AIExecution(Base):
    """AI execution record.

    Stores execution metadata for prompt package processing.
    Links to prompt_packages for context.
    """
    __tablename__ = "ai_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    raw_response = Column(Text, nullable=True)
    parsed_response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    prompt_package = relationship("PromptPackage", backref="ai_executions")

    __table_args__ = (
        Index("ix_ai_executions_user_created", "user_id", "created_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
