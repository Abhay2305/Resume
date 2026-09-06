"""Repositories package for data access layer."""
from .base import BaseRepository
from .identity import (
    DeviceRepository,
    LoginHistoryRepository,
    OAuthAccountRepository,
    OrganizationRepository,
    PermissionRepository,
    RoleRepository,
    SessionRepository,
    UserPreferenceRepository,
    UserRepository,
    UserRoleRepository,
    ProfileRepository,
    get_repositories,
)
from .audit import (
    AuditArchiveRepository,
    AuditConfigRepository,
    AuditExportRepository,
    AuditLogRepository,
    get_audit_repositories,
)
from .error import (
    ErrorArchiveRepository,
    ErrorCategoryRepository,
    ErrorLogRepository,
    ErrorOccurrenceRepository,
    ErrorResolutionRepository,
    get_error_repositories,
)
from .ai_execution import AIExecutionRepository
from .ai_response_intelligence import (
    AIResponseValidationRepository,
    ResumeDiffRepository,
    ChangeSetRepository,
    ValidationReportRepository,
    ConfidenceScoreRepository,
)
from .pipeline import PipelineRunRepository, PipelineStageRepository
from .config import ConfigRepository, FeatureFlagRepository
from .metric import MetricRepository

__all__ = [
    "BaseRepository",
    "DeviceRepository",
    "LoginHistoryRepository",
    "OAuthAccountRepository",
    "OrganizationRepository",
    "PermissionRepository",
    "ProfileRepository",
    "RoleRepository",
    "SessionRepository",
    "UserPreferenceRepository",
    "UserRepository",
    "UserRoleRepository",
    "get_repositories",
    "AuditArchiveRepository",
    "AuditConfigRepository",
    "AuditExportRepository",
    "AuditLogRepository",
    "get_audit_repositories",
    "ErrorArchiveRepository",
    "ErrorCategoryRepository",
    "ErrorLogRepository",
    "ErrorOccurrenceRepository",
    "ErrorResolutionRepository",
    "get_error_repositories",
    "AIExecutionRepository",
    "AIResponseValidationRepository",
    "ResumeDiffRepository",
    "ChangeSetRepository",
    "ValidationReportRepository",
    "ConfidenceScoreRepository",
    "PipelineRunRepository",
    "PipelineStageRepository",
    "ConfigRepository",
    "FeatureFlagRepository",
    "MetricRepository",
]
