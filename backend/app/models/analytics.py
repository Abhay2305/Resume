"""Analysis domain models (existing tables only in this step).

Contains the existing ATSResult table, moved here unchanged. user_analytics
and export_history are introduced in a later Phase 2 commit.
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


class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    score = Column(Integer, nullable=False)
    details = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="ats_results")
