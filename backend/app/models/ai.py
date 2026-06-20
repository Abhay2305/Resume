"""AI domain models (existing tables only in this step).

Contains the existing CoverLetter, AIRequest and ResumeRule tables, moved here
unchanged. The separated four-stage AI lifecycle (ai_requests / prompt_history
/ knowledge_retrievals / ai_generations) and ai_models are introduced in a
later Phase 2 commit.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .base import Base


class CoverLetter(Base):
    __tablename__ = "cover_letters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False, default="Untitled Cover Letter")
    job_role = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    experience_summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cover_letters")


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    request_type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_requests")


class ResumeRule(Base):
    __tablename__ = "resume_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(50), nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=False)
    rule_prompt_instruction = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
