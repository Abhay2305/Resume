"""Domain-split ORM models package.

This package replaces the former single ``models.py`` module. Models are
organized by bounded context (domain) for long-term maintainability as the
schema grows past 30 tables:

- identity     -> User, Profile, Subscription, Payment, Session, Device,
                  LoginHistory, OAuthAccount, Role, Permission, UserRole,
                  RolePermission, Organization, OrganizationMember, UserPreference
- audit        -> AuditLog, AuditConfig, AuditArchive, AuditExport
- error        -> ErrorLog, ErrorCategory, ErrorResolution, ErrorArchive, ErrorOccurrence
- resume       -> Resume, ResumeSection, ResumeVersion, Template
- ai           -> CoverLetter, AIRequest, ResumeRule
- analytics    -> ATSResult
- settings     -> ActivityLog

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

# Identity domain - Core
from .identity import (
    User,
    Profile,
    Subscription,
    Payment,
)

# Identity domain - Security & Sessions
from .identity import (
    UserSession,
    Device,
    LoginHistory,
    OAuthAccount,
)

# Identity domain - RBAC
from .identity import (
    Role,
    Permission,
    UserRole,
    RolePermission,
)

# Identity domain - Organizations
from .identity import (
    Organization,
    OrganizationMember,
)

# Identity domain - Preferences
from .identity import (
    UserPreference,
)

# Audit domain
from .audit import AuditLog, AuditConfig, AuditArchive, AuditExport

# Error domain
from .error import ErrorLog, ErrorCategory, ErrorResolution, ErrorArchive, ErrorOccurrence

# Resume domain
from .resume import Resume, ResumeSection, ResumeVersion, Template, TemplateVersion

# AI domain
from .ai import CoverLetter, AIRequest, ResumeRule

# Analysis domain
from .analytics import ATSResult

# Platform domain
from .settings import ActivityLog

# Opportunity Intelligence Engine
from .opportunity import Opportunity, ParsedOpportunityData, OpportunityEntity

# Resume Intelligence Engine
from .resume_intelligence import ResumeProfile, ParsedResumeData, ResumeEntity as ResumeIntelligenceEntity, ResumeKnowledge

# Gap Analysis Engine
from .gap_analysis import GapAnalysis, GapResult, Recommendation

# Knowledge Intelligence Engine
from .knowledge_intelligence import KnowledgeDocument, KnowledgeSection, KnowledgeRule, KnowledgeRetrieval, KnowledgeContext

# Prompt Intelligence Engine
from .prompt_intelligence import PromptTemplate, PromptPackage, PromptVariable, PromptExecution, PromptVersion

# AI Execution Engine
from .ai_execution import AIExecution

# AI Response Intelligence Engine
from .ai_response_intelligence import (
    AIResponseValidation,
    ResumeDiff,
    ChangeSet,
    ValidationReport,
    ConfidenceScore,
    ValidationStatus,
    ChangeType,
    ChangeCategory,
    RiskLevel,
)

# Pipeline Intelligence Engine
from .pipeline import PipelineRun, PipelineStage

# PROCS domain (Operations & Control System)
from .config import SystemConfig, FeatureFlag

# Metrics domain
from .metric import SystemMetric

__all__ = [
    # Base
    "Base",
    "UUIDPrimaryKeyMixin",
    "TimestampMixin",
    "MetadataMixin",
    "SoftDeleteMixin",
    "generate_uuid",
    # Identity - Core
    "User",
    "Profile",
    "Subscription",
    "Payment",
    # Identity - Security & Sessions
    "UserSession",
    "Device",
    "LoginHistory",
    "OAuthAccount",
    # Identity - RBAC
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    # Identity - Organizations
    "Organization",
    "OrganizationMember",
    # Identity - Preferences
    "UserPreference",
    # Audit domain
    "AuditLog",
    "AuditConfig",
    "AuditArchive",
    "AuditExport",
    # Error domain
    "ErrorLog",
    "ErrorCategory",
    "ErrorResolution",
    "ErrorArchive",
    "ErrorOccurrence",
    # Resume domain
    "Resume",
    "ResumeSection",
    "ResumeVersion",
    "Template",
    # AI domain
    "CoverLetter",
    "AIRequest",
    "ResumeRule",
    # Analytics domain
    "ATSResult",
    # Settings domain
    "ActivityLog",
    # Opportunity Intelligence Engine
    "Opportunity",
    "ParsedOpportunityData",
    "OpportunityEntity",
    # Resume Intelligence Engine
    "ResumeProfile",
    "ParsedResumeData",
    "ResumeKnowledge",
    # Gap Analysis Engine
    "GapAnalysis",
    "GapResult",
    "Recommendation",
    # Knowledge Intelligence Engine
    "KnowledgeDocument",
    "KnowledgeSection",
    "KnowledgeRule",
    "KnowledgeRetrieval",
    "KnowledgeContext",
    # Prompt Intelligence Engine
    "PromptTemplate",
    "PromptPackage",
    "PromptVariable",
    "PromptExecution",
    "PromptVersion",
    # AI Execution Engine
    "AIExecution",
    # AI Response Intelligence Engine
    "AIResponseValidation",
    "ResumeDiff",
    "ChangeSet",
    "ValidationReport",
    "ConfidenceScore",
    "ValidationStatus",
    "ChangeType",
    "ChangeCategory",
    "RiskLevel",
    # Pipeline Intelligence Engine
    "PipelineRun",
    "PipelineStage",
    # PROCS domain
    "SystemConfig",
    "FeatureFlag",
    # Metrics domain
    "SystemMetric",
]
