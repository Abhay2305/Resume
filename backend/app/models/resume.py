"""Resume domain models (existing tables only in this step).

The normalized, immutable versioning redesign (resume_version_sections,
lineage, snapshot_json) is introduced in a later Phase 2 commit. Here the
existing Resume, ResumeSection, ResumeVersion and Template tables are moved
unchanged as part of the non-breaking domain split.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Index,
    String,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False, default="Untitled Resume")
    template_id = Column(
        String(100), ForeignKey("templates.id", ondelete="SET NULL"), nullable=True
    )
    section_order = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="resumes")
    template = relationship("Template", back_populates="resumes")
    sections = relationship(
        "ResumeSection",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeSection.position",
    )
    versions = relationship(
        "ResumeVersion", back_populates="resume", cascade="all, delete-orphan"
    )
    ats_results = relationship(
        "ATSResult", back_populates="resume", cascade="all, delete-orphan"
    )


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    section_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    position = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resume = relationship("Resume", back_populates="sections")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    version_number = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="versions")


class Template(Base):
    """Dynamic resume template with full CMS support.

    Templates are versioned, publishable entities. Only 'published' templates
    appear in the Prompt Resume frontend. Admins can upload thumbnails, preview
    images, and template definitions without code changes.
    """
    __tablename__ = "templates"
    __table_args__ = (
        Index("ix_templates_status_sort", "status", "sort_order"),
    )

    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), nullable=True, unique=True, index=True)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False)

    # Media
    thumbnail_url = Column(String(500), nullable=True)
    preview_images = Column(JSON, nullable=True)  # List of preview image URLs

    # Template definition (the JSON that the renderer interprets)
    color_scheme = Column(JSON, nullable=False)
    layout_schema = Column(JSON, nullable=False)
    template_definition = Column(JSON, nullable=True)  # Full template JSON for advanced rendering

    # Appearance
    theme = Column(String(50), nullable=True)  # light, dark
    fonts = Column(JSON, nullable=True)  # {heading: "...", body: "...", mono: "..."}
    colors = Column(JSON, nullable=True)  # Extended color palette

    # Lifecycle
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft, published, archived, deprecated
    version = Column(Integer, nullable=False, default=1)
    author = Column(String(100), nullable=True)
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0, index=True)

    # Discovery
    tags = Column(JSON, nullable=True)  # List of tag strings
    usage_count = Column(Integer, default=0)

    # Metadata
    metadata_json = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    resumes = relationship("Resume", back_populates="template")
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")


class TemplateVersion(Base):
    """Template version history snapshot.

    Each time a template is published or significantly updated,
    a version snapshot is created for rollback support.
    """
    __tablename__ = "template_versions"
    __table_args__ = (
        UniqueConstraint("template_id", "version", name="uq_template_version"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(
        String(100), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, nullable=False)
    snapshot = Column(JSON, nullable=False)  # Full template state at this version
    created_at = Column(DateTime, default=datetime.utcnow)

    template = relationship("Template", back_populates="versions")
