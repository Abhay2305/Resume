"""Configuration domain models.

Contains system configuration and feature flag models for the PROCS
(Operations & Control System). These models store all configurable
settings in the database, enabling dynamic configuration without
code changes.

Design Principles:
- All primary keys are UUID strings (36 chars)
- Timestamps (created_at, updated_at) on all mutable entities
- Unique constraints on business keys (key, name)
- Indexes on frequently queried columns
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from .base import Base


class SystemConfig(Base):
    """System configuration key-value store.

    Stores application settings organized by category. Supports:
    - Key-value configuration with categories
    - Public/private visibility
    - Version tracking for audit trails
    - Automatic timestamp management
    """

    __tablename__ = "system_config"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(200), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    version = Column(Integer, default=1, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class FeatureFlag(Base):
    """Feature flag for gradual rollout and A/B testing.

    Supports:
    - Enable/disable toggles
    - Percentage-based rollout
    - Tier-based access control
    - Environment-specific flags
    - Automatic timestamp management
    """

    __tablename__ = "feature_flags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=False, nullable=False)
    rollout_percentage = Column(Integer, default=100, nullable=False)
    allowed_tiers = Column(Text, nullable=True)  # JSON string for SQLite compat
    environment = Column(String(50), default="all", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
