"""Resume Intelligence Engine models.

This module defines the database models for the Resume Intelligence Engine.
It includes enums for status and entity types, and three ORM models:
- ResumeProfile: The main resume record
- ParsedResumeData: Structured data extracted from parsing
- ResumeEntity: Normalized entities (skills, technologies, etc.)
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


class ResumeProfileStatus(str, Enum):
    """Status of a resume profile through the parsing pipeline."""
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ResumeEntityType(str, Enum):
    """Types of entities that can be extracted from a resume."""
    PERSONAL_INFO = "personal_info"
    CONTACT = "contact"
    SKILL = "skill"
    TECHNOLOGY = "technology"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD_PLATFORM = "cloud_platform"
    DEVOPS_TOOL = "devops_tool"
    AI_ML = "ai_ml"
    CERTIFICATION = "certification"
    EDUCATION = "education"
    PROJECT = "project"
    ACHIEVEMENT = "achievement"
    EXPERIENCE = "experience"
    COMPANY = "company"
    ROLE = "role"
    METRIC = "metric"
    DATE = "date"
    DEGREE = "degree"
    FIELD_OF_STUDY = "field_of_study"


class ResumeProfile(Base):
    """Main resume profile record.

    Stores the raw resume text and metadata about the parsing process.
    """
    __tablename__ = "resume_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default=ResumeProfileStatus.PENDING.value, index=True)
    error_message = Column(Text, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    parser_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Relationships
    parsed_data = relationship(
        "ParsedResumeData",
        back_populates="resume_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    entities = relationship(
        "ResumeEntity",
        back_populates="resume_profile",
        cascade="all, delete-orphan",
    )
    knowledge = relationship(
        "ResumeKnowledge",
        back_populates="resume_profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user = relationship("User", foreign_keys=[user_id])


class ParsedResumeData(Base):
    """Structured data extracted from parsing a resume.

    Contains non-entity data like summary, experience entries, education entries,
    and raw sections. Entities (skills, technologies, etc.) are stored in the ResumeEntity table.
    """
    __tablename__ = "parsed_resume_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_profile_id = Column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    summary = Column(Text, nullable=True)
    experience_entries = Column(JSON, nullable=True)
    education_entries = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    raw_sections = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    resume_profile = relationship("ResumeProfile", back_populates="parsed_data")


class ResumeEntity(Base):
    """Normalized entity extracted from a resume.

    Each row represents a single extracted entity (e.g., one skill, one technology).
    This enables efficient querying across resumes.
    """
    __tablename__ = "resume_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_profile_id = Column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type = Column(String(50), nullable=False, index=True)
    entity_value = Column(String(255), nullable=False, index=True)
    entity_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    resume_profile = relationship("ResumeProfile", back_populates="entities")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class ResumeKnowledge(Base):
    """Structured Resume Knowledge representation.

    The canonical understanding of a user's resume. Future phases must consume
    this instead of reparsing the resume.
    """
    __tablename__ = "resume_knowledge"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_profile_id = Column(
        String(36),
        ForeignKey("resume_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    personal_info = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)
    technologies = Column(JSON, nullable=True)
    experience_summary = Column(JSON, nullable=True)
    education_summary = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    achievements = Column(JSON, nullable=True)
    total_experience_years = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    resume_profile = relationship("ResumeProfile", back_populates="knowledge")
