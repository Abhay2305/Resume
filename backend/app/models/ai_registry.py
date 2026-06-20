"""AI model registry (new in Phase 2).

Kept in its own module to avoid disturbing the existing ai.py during the
additive rollout. Re-exported from models/__init__ alongside the AI domain.

Every AI execution references a row here instead of hardcoding a provider, so
providers/models can change over time without rewriting historical records.
"""
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    MetadataMixin,
    SoftDeleteMixin,
)


class AIModel(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A registered LLM/embedding model available to the platform."""

    __tablename__ = "ai_models"

    provider = Column(String(100), nullable=False)  # gemini|openai|anthropic|...
    model_name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=True)
    kind = Column(String(50), nullable=False, default="generation")  # generation|embedding
    context_window = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    generations = relationship("AIGeneration", back_populates="model")
