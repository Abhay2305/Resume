"""Opportunity Intelligence Engine models.

This module defines the database models for the Opportunity Intelligence Engine.
It includes enums for status and entity types, and three ORM models:
- Opportunity: The main opportunity record
- ParsedOpportunityData: Structured data extracted from parsing
- OpportunityEntity: Normalized entities (skills, technologies, etc.)
"""
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class OpportunityStatus(str, Enum):
    """Status of an opportunity through the parsing pipeline."""
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"
    ARCHIVED = "archived"


class EntityType(str, Enum):
    """Types of entities that can be extracted from an opportunity."""
    SKILL = "skill"
    TECHNOLOGY = "technology"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD_PLATFORM = "cloud_platform"
    DEVOPS_TOOL = "devops_tool"
    AI_ML = "ai_ml"
    CERTIFICATION = "certification"
    SOFT_SKILL = "soft_skill"
    EDUCATION = "education"
    LOCATION = "location"
    EMPLOYMENT_TYPE = "employment_type"
    REMOTE_POLICY = "remote_policy"
    EXPERIENCE_LEVEL = "experience_level"


class Opportunity(Base):
    """Main opportunity record.

    Stores the raw opportunity description and metadata about the parsing process.
    """
    __tablename__ = "opportunities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    raw_text = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    url = Column(String(1024), nullable=True)
    status = Column(String(50), nullable=False, default=OpportunityStatus.PENDING.value, index=True)
    error_message = Column(Text, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    parser_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    parsed_data = relationship(
        "ParsedOpportunityData",
        back_populates="opportunity",
        uselist=False,
        cascade="all, delete-orphan",
    )
    entities = relationship(
        "OpportunityEntity",
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
    user = relationship("User", back_populates="opportunities", foreign_keys=[user_id])


class ParsedOpportunityData(Base):
    """Structured data extracted from parsing an opportunity.

    Contains non-entity data like responsibilities, benefits, and raw sections.
    Entities (skills, technologies, etc.) are stored in the OpportunityEntity table.
    """
    __tablename__ = "parsed_opportunity_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(
        String(36),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    responsibilities = Column(JSON, nullable=True)
    benefits = Column(JSON, nullable=True)
    ats_keywords = Column(JSON, nullable=True)
    raw_sections = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="parsed_data")


class OpportunityEntity(Base):
    """Normalized entity extracted from an opportunity.

    Each row represents a single extracted entity (e.g., one skill, one technology).
    This enables efficient querying across opportunities.
    """
    __tablename__ = "opportunity_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(
        String(36),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type = Column(String(50), nullable=False, index=True)
    entity_value = Column(String(255), nullable=False, index=True)
    is_required = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    opportunity = relationship("Opportunity", back_populates="entities")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
