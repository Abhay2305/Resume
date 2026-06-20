"""Domain-split ORM models package.

This package replaces the former single ``models.py`` module. Models are
organized by bounded context (domain) for long-term maintainability as the
schema grows past 30 tables:

- identity     -> User, Profile, Subscription, Payment
- resume       -> Resume, ResumeSection, ResumeVersion, Template
- ai           -> CoverLetter, AIRequest, ResumeRule
- analytics    -> ATSResult
- settings     -> ActivityLog

New memory-layer tables (conversation, knowledge, separated AI lifecycle,
normalized version sections, settings/analytics, ai_models) are added in
subsequent Phase 2 commits within their respective domain modules.

Every model and the shared ``Base`` are re-exported here so that existing
imports such as ``from .models import User`` and ``from .models import Base``
continue to work unchanged. This keeps the refactor strictly non-breaking.
"""
from .base import Base
from .mixins import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    MetadataMixin,
    SoftDeleteMixin,
    generate_uuid,
)

# Identity domain
from .identity import User, Profile, Subscription, Payment

# Resume domain
from .resume import Resume, ResumeSection, ResumeVersion, Template

# AI domain
from .ai import CoverLetter, AIRequest, ResumeRule

# Analysis domain
from .analytics import ATSResult

# Platform domain
from .settings import ActivityLog

__all__ = [
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "MetadataMixin",
    "SoftDeleteMixin",
    "generate_uuid",
    "User",
    "Profile",
    "Subscription",
    "Payment",
    "Resume",
    "ResumeSection",
    "ResumeVersion",
    "Template",
    "CoverLetter",
    "AIRequest",
    "ResumeRule",
    "ATSResult",
    "ActivityLog",
]
