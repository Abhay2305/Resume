"""Resume domain models (existing tables only in this step).

The normalized, immutable versioning redesign (resume_version_sections,
lineage, snapshot_json) is introduced in a later Phase 2 commit. Here the
existing Resume, ResumeSection, ResumeVersion and Template tables are moved
unchanged as part of the non-breaking domain split.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
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
    __tablename__ = "templates"

    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    preview_image = Column(String(255), nullable=True)
    color_scheme = Column(JSON, nullable=False)
    layout_schema = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="template")
