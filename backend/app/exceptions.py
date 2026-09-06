"""Application exception hierarchy.

All custom exceptions inherit from ApplicationException, which carries
structured error context and maps to standardized HTTP responses.

Usage in services:
    from app.exceptions import NotFoundError, ValidationError, ForbiddenError
    raise NotFoundError(message="User not found", details={"user_id": user_id})
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ErrorDetail:
    """Individual error detail for field-level errors."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

    def to_dict(self) -> Dict[str, str]:
        return {"field": self.field, "message": self.message}


class ApplicationException(Exception):
    """Base exception for all application errors.

    Every application exception exposes:
    - HTTP Status Code
    - Error Code
    - Human-readable Message
    - Optional Details
    - request_id (populated from context)
    - Timestamp
    """

    status_code: int = 500
    default_code: str = "INTERNAL_ERROR"
    _sensitive_fields: tuple = ()

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[List[ErrorDetail]] = None,
    ):
        self.message = message
        self.code = code or self.default_code
        self.details = details or {}
        self.errors = errors or []
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.request_id: Optional[str] = None
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to standardized error response."""
        result: Dict[str, Any] = {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "request_id": self.request_id,
                "timestamp": self.timestamp,
            },
        }
        if self.errors:
            result["error"]["errors"] = [e.to_dict() for e in self.errors]
        return result


# ---------------------------------------------------------------------------
# 4xx Client Errors
# ---------------------------------------------------------------------------

class BadRequestError(ApplicationException):
    """400 — Invalid request (malformed JSON, missing fields)."""
    status_code = 400
    default_code = "BAD_REQUEST"


class ValidationError(ApplicationException):
    """422 — Input validation failed."""
    status_code = 422
    default_code = "VALIDATION_ERROR"


class AuthenticationError(ApplicationException):
    """401 — Authentication required or failed."""
    status_code = 401
    default_code = "AUTHENTICATION_ERROR"


class AuthorizationError(ApplicationException):
    """403 — Authenticated but not authorized."""
    status_code = 403
    default_code = "AUTHORIZATION_ERROR"


class NotFoundError(ApplicationException):
    """404 — Resource not found."""
    status_code = 404
    default_code = "NOT_FOUND"


class ConflictError(ApplicationException):
    """409 — Resource already exists or state conflict."""
    status_code = 409
    default_code = "CONFLICT"


class BusinessRuleError(ApplicationException):
    """400 — Business rule violation."""
    status_code = 400
    default_code = "BUSINESS_RULE_ERROR"


class RateLimitError(ApplicationException):
    """429 — Rate limit exceeded."""
    status_code = 429
    default_code = "RATE_LIMIT_EXCEEDED"


# ---------------------------------------------------------------------------
# 5xx Server Errors
# ---------------------------------------------------------------------------

class InternalServerError(ApplicationException):
    """500 — Unexpected internal error."""
    status_code = 500
    default_code = "INTERNAL_ERROR"


class ServiceUnavailableError(ApplicationException):
    """503 — External service unavailable (AI provider, storage, etc.)."""
    status_code = 503
    default_code = "SERVICE_UNAVAILABLE"


class TimeoutError(ApplicationException):
    """504 — Operation timed out."""
    status_code = 504
    default_code = "TIMEOUT"


class ExternalServiceError(ApplicationException):
    """502 — External service unavailable (AI provider, storage, etc.)."""
    status_code = 502
    default_code = "EXTERNAL_SERVICE_ERROR"


class DatabaseError(ApplicationException):
    """500 — Database operation errors."""
    status_code = 500
    default_code = "DATABASE_ERROR"


class FileStorageError(ApplicationException):
    """500 — File storage operation errors."""
    status_code = 500
    default_code = "FILE_STORAGE_ERROR"
