"""Prompt Intelligence Engine domain models.

Constructs deterministic, explainable, provider-agnostic prompts.
No AI execution - only prompt preparation.
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
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class PromptTemplate(Base):
    """Prompt template definition.

    Stores reusable prompt templates with versioning.
    """
    __tablename__ = "prompt_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    prompt_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    is_active = Column(Boolean, nullable=False, default=True)
    variables = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    packages = relationship("PromptPackage", back_populates="template")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class PromptPackage(Base):
    """Assembled prompt package.

    The complete, validated prompt ready for AI execution.
    """
    __tablename__ = "prompt_packages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(
        String(36),
        ForeignKey("prompt_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    prompt_type = Column(String(50), nullable=False, index=True)
    system_prompt = Column(Text, nullable=False)
    resume_context = Column(JSON, nullable=True)
    opportunity_context = Column(JSON, nullable=True)
    gap_context = Column(JSON, nullable=True)
    knowledge_context = Column(JSON, nullable=True)
    instructions = Column(JSON, nullable=True)
    constraints = Column(JSON, nullable=True)
    output_schema = Column(JSON, nullable=True)
    total_tokens_estimate = Column(Integer, nullable=True)
    is_validated = Column(Boolean, nullable=False, default=False)
    validation_errors = Column(JSON, nullable=True)
    version = Column(String(20), nullable=False, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    template = relationship("PromptTemplate", back_populates="packages")
    executions = relationship("PromptExecution", back_populates="package", cascade="all, delete-orphan")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class PromptVariable(Base):
    """Prompt variable definition.

    Stores variables used in prompt templates.
    """
    __tablename__ = "prompt_variables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    variable_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    variable_type = Column(String(50), nullable=False, default="string")
    default_value = Column(Text, nullable=True)
    is_required = Column(Boolean, nullable=False, default=True)
    source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_prompt_variables_type", "variable_type"),
        Index("ix_prompt_variables_source", "source"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class PromptExecution(Base):
    """Prompt execution record (metadata only).

    Tracks prompt executions without storing AI responses.
    """
    __tablename__ = "prompt_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id = Column(
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
    status = Column(String(20), nullable=False, default="pending")
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    total_tokens = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    package = relationship("PromptPackage", back_populates="executions")

    __table_args__ = (
        Index("ix_prompt_executions_status", "status"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class PromptVersion(Base):
    """Prompt version history.

    Tracks prompt evolution across template, rule, and knowledge versions.
    """
    __tablename__ = "prompt_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(
        String(36),
        ForeignKey("prompt_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(String(20), nullable=False)
    system_prompt_hash = Column(String(64), nullable=True)
    template_version = Column(String(20), nullable=True)
    rules_version = Column(String(20), nullable=True)
    knowledge_version = Column(String(20), nullable=True)
    changes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("template_id", "version", name="uq_prompt_version_template_version"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
