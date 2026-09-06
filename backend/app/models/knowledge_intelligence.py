"""Knowledge Intelligence Engine domain models.

Manages knowledge documents, sections, rules, retrievals, and contexts.
No AI involved - deterministic knowledge retrieval based on gap analysis.
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


class KnowledgeDocument(Base):
    """Knowledge document metadata.

    Stores information about knowledge sources (Harvard, MIT, Yale, etc.)
    without duplicating the actual PDF content.
    """
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False, index=True)
    version = Column(String(20), nullable=False, default="1.0")
    description = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=0.8)
    is_active = Column(Boolean, nullable=False, default=True)
    total_rules = Column(Integer, nullable=True, default=0)
    total_sections = Column(Integer, nullable=True, default=0)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sections = relationship("KnowledgeSection", back_populates="document", cascade="all, delete-orphan")
    rules = relationship("KnowledgeRule", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_knowledge_documents_source", "source"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class KnowledgeSection(Base):
    """Knowledge section within a document.

    Represents a section or chapter of a knowledge document.
    """
    __tablename__ = "knowledge_sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(
        String(36),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_key = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content_summary = Column(Text, nullable=True)
    rule_count = Column(Integer, nullable=True, default=0)
    sort_order = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("KnowledgeDocument", back_populates="sections")
    rules = relationship("KnowledgeRule", back_populates="section", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("document_id", "section_key", name="uq_knowledge_section_doc_key"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class KnowledgeRule(Base):
    """Structured knowledge rule.

    Every rule is normalized with: rule_id, source, section, priority,
    category, instruction, reason, and examples.
    Provenance fields track lineage from PDF to active rule.
    """
    __tablename__ = "knowledge_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(
        String(36),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_id = Column(
        String(36),
        ForeignKey("knowledge_sections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rule_key = Column(String(100), nullable=False, unique=True, index=True)
    source = Column(String(255), nullable=False)
    section_name = Column(String(100), nullable=False, index=True)
    priority = Column(String(20), nullable=False, default="medium", index=True)
    category = Column(String(50), nullable=False, index=True)
    instruction = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    examples = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    confidence = Column(Float, nullable=False, default=0.8)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Provenance fields
    source_document = Column(String(255), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_section = Column(String(100), nullable=True)
    source_evidence = Column(Text, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    extraction_timestamp = Column(String(30), nullable=True)
    rule_hash = Column(String(64), nullable=True, index=True)
    state = Column(String(20), nullable=False, default="ACTIVE", index=True)
    version = Column(Integer, nullable=False, default=1)

    # Relationships
    document = relationship("KnowledgeDocument", back_populates="rules")
    section = relationship("KnowledgeSection", back_populates="rules")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class KnowledgeRetrieval(Base):
    """Knowledge retrieval record.

    Tracks what rules were retrieved for a specific gap analysis.
    """
    __tablename__ = "knowledge_retrievals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_rules_retrieved = Column(Integer, nullable=False, default=0)
    retrieval_strategy = Column(String(50), nullable=False, default="category_match")
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    context = relationship("KnowledgeContext", back_populates="retrieval", uselist=False)

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )


class KnowledgeContext(Base):
    """Structured knowledge context.

    The output of the Knowledge Intelligence Engine: a structured collection
    of rules organized by section, ready for prompt building.
    """
    __tablename__ = "knowledge_contexts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    retrieval_id = Column(
        String(36),
        ForeignKey("knowledge_retrievals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    gap_analysis_id = Column(
        String(36),
        ForeignKey("gap_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary_rules = Column(Text, nullable=True)
    experience_rules = Column(Text, nullable=True)
    skills_rules = Column(Text, nullable=True)
    education_rules = Column(Text, nullable=True)
    projects_rules = Column(Text, nullable=True)
    certifications_rules = Column(Text, nullable=True)
    ats_rules = Column(Text, nullable=True)
    formatting_rules = Column(Text, nullable=True)
    cover_letter_rules = Column(Text, nullable=True)
    total_rules = Column(Integer, nullable=False, default=0)
    citations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    retrieval = relationship("KnowledgeRetrieval", back_populates="context")

    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )
