"""Error domain service.

Provides high-level error logging and management operations.
Handles exception capture, categorization, and resolution workflows.
"""
import json
import os
import platform
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.error import ErrorLog
from ..repositories.error import (
    ErrorArchiveRepository,
    ErrorCategoryRepository,
    ErrorLogRepository,
    ErrorOccurrenceRepository,
    ErrorResolutionRepository,
)


class ErrorService:
    """Service for error logging and management.

    Usage:
        service = ErrorService(db)
        service.log_exception(e, context={...})
    """

    def __init__(self, db: Session):
        self.db = db
        self.logs = ErrorLogRepository(db)
        self.categories = ErrorCategoryRepository(db)
        self.resolutions = ErrorResolutionRepository(db)
        self.occurrences = ErrorOccurrenceRepository(db)
        self.archives = ErrorArchiveRepository(db)

    # -----------------------------------------------------------------------
    # Exception logging methods
    # -----------------------------------------------------------------------

    def log_exception(
        self,
        exc: Exception,
        *,
        context: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_payload: Optional[str] = None,
        response_status: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        cover_letter_id: Optional[str] = None,
        environment: Optional[str] = None,
        router: Optional[str] = None,
    ) -> ErrorLog:
        """Log an exception with full context."""
        # Extract exception details
        error_type = type(exc).__name__
        error_message = str(exc)
        stack_trace = traceback.format_exc()

        # Extract source location from traceback
        tb = exc.__traceback__
        module = None
        function = None
        file_path = None
        line_number = None
        if tb:
            frame = tb.tb_frame
            module = frame.f_code.co_filename
            function = frame.f_code.co_name
            file_path = module
            line_number = tb.tb_lineno

        # Determine severity based on exception type
        severity = self._determine_severity(exc)

        # Auto-categorize
        category = self.categories.auto_categorize(error_type, error_message)
        category_id = category.id if category else None

        # Get environment
        env = environment or os.getenv("ENVIRONMENT", "development")

        # Get system info
        python_version = platform.python_version()
        db_provider = os.getenv("DATABASE_URL", "sqlite").split(":")[0]
        ai_provider = os.getenv("AI_PROVIDER", None)
        app_version = os.getenv("APP_VERSION", "1.0.0")

        return self.logs.log(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            module=module,
            function=function,
            file_path=file_path,
            line_number=line_number,
            endpoint=endpoint,
            http_method=http_method,
            request_payload=self._redact_sensitive(request_payload),
            response_status=response_status,
            ip_address=ip_address,
            user_agent=user_agent,
            processing_time_ms=processing_time_ms,
            severity=severity,
            environment=env,
            python_version=python_version,
            database_provider=db_provider,
            ai_provider=ai_provider,
            app_version=app_version,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            correlation_id=correlation_id,
            resume_id=resume_id,
            cover_letter_id=cover_letter_id,
            category_id=category_id,
            metadata_json=json.dumps(context) if context else None,
            router=router,
        )

    def log_error(
        self,
        *,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        module: Optional[str] = None,
        function: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_payload: Optional[str] = None,
        response_status: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        severity: str = "medium",
        environment: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        cover_letter_id: Optional[str] = None,
        metadata_json: Optional[str] = None,
        router: Optional[str] = None,
    ) -> ErrorLog:
        """Log a handled error with explicit details."""
        env = environment or os.getenv("ENVIRONMENT", "development")
        python_version = platform.python_version()
        db_provider = os.getenv("DATABASE_URL", "sqlite").split(":")[0]
        ai_provider = os.getenv("AI_PROVIDER", None)
        app_version = os.getenv("APP_VERSION", "1.0.0")

        return self.logs.log(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            module=module,
            function=function,
            file_path=file_path,
            line_number=line_number,
            endpoint=endpoint,
            http_method=http_method,
            request_payload=self._redact_sensitive(request_payload),
            response_status=response_status,
            ip_address=ip_address,
            user_agent=user_agent,
            processing_time_ms=processing_time_ms,
            severity=severity,
            environment=env,
            python_version=python_version,
            database_provider=db_provider,
            ai_provider=ai_provider,
            app_version=app_version,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            correlation_id=correlation_id,
            resume_id=resume_id,
            cover_letter_id=cover_letter_id,
            metadata_json=metadata_json,
            router=router,
        )

    def log_api_error(
        self,
        *,
        status_code: int,
        detail: str,
        endpoint: str,
        http_method: str,
        request_payload: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        router: Optional[str] = None,
    ) -> ErrorLog:
        """Log an API error (4xx/5xx responses)."""
        severity = self._determine_status_severity(status_code)
        return self.log_error(
            error_type=f"HTTPError_{status_code}",
            error_message=detail,
            endpoint=endpoint,
            http_method=http_method,
            request_payload=request_payload,
            response_status=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
            processing_time_ms=processing_time_ms,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            correlation_id=correlation_id,
            router=router,
        )

    # -----------------------------------------------------------------------
    # Query methods
    # -----------------------------------------------------------------------

    def get_error(self, error_id: str) -> Optional[ErrorLog]:
        """Get error by ID."""
        return self.logs.get(error_id)

    def get_error_history(
        self,
        *,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ErrorLog]:
        """Get error history with filters."""
        if user_id:
            return self.logs.get_by_user(user_id, limit=limit, offset=offset, status=status)
        if severity:
            return self.logs.get_by_severity(severity, start=start, end=end, limit=limit)
        if status:
            return self.logs.get_by_status(status, limit=limit, offset=offset)
        if error_type:
            return self.logs.get_by_entity(error_type, limit=limit, offset=offset)
        return self.logs.get_by_time_range(
            start or datetime.min, end or datetime.utcnow(), limit=limit
        )

    def get_unresolved_errors(
        self, *, severity: Optional[str] = None, limit: int = 100
    ) -> List[ErrorLog]:
        """Get unresolved errors."""
        return self.logs.get_unresolved(severity=severity, limit=limit)

    def get_critical_errors(
        self, *, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> List[ErrorLog]:
        """Get critical errors."""
        return self.logs.get_critical_errors(start=start, end=end)

    def get_error_statistics(
        self, *, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        return self.logs.get_statistics(start=start, end=end)

    def get_error_summary(
        self, *, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get error summary for dashboard."""
        stats = self.get_error_statistics(start=start, end=end)
        return {
            "total_errors": stats["total_count"],
            "by_severity": stats["by_severity"],
            "by_status": stats["by_status"],
            "top_types": stats["top_types"],
            "resolution_rate": self._calculate_resolution_rate(start, end),
        }

    def search_errors(
        self,
        query: str,
        *,
        limit: int = 50,
    ) -> List[ErrorLog]:
        """Search errors by message or type."""
        return (
            self.db.query(ErrorLog)
            .filter(
                (ErrorLog.error_message.ilike(f"%{query}%"))
                | (ErrorLog.error_type.ilike(f"%{query}%"))
            )
            .order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )

    # -----------------------------------------------------------------------
    # Resolution workflow
    # -----------------------------------------------------------------------

    def acknowledge_error(
        self,
        error_id: str,
        assigned_to: Optional[str] = None,
    ) -> Optional[ErrorLog]:
        """Acknowledge an error and optionally assign it."""
        return self.logs.update_status(error_id, "acknowledged")

    def start_investigation(
        self,
        error_id: str,
        assigned_to: Optional[str] = None,
    ) -> Optional[ErrorLog]:
        """Start investigating an error."""
        return self.logs.update_status(error_id, "investigating")

    def resolve_error(
        self,
        error_id: str,
        *,
        resolution_type: str,
        title: str,
        description: Optional[str] = None,
        root_cause: Optional[str] = None,
        fix_commit: Optional[str] = None,
        fix_pr: Optional[str] = None,
        prevention_notes: Optional[str] = None,
        test_added: bool = False,
        assigned_to: Optional[str] = None,
    ) -> Optional[ErrorLog]:
        """Resolve an error with a resolution record."""
        # Create resolution
        resolution = self.resolutions.create(
            {
                "resolution_type": resolution_type,
                "title": title,
                "description": description,
                "root_cause": root_cause,
                "fix_commit": fix_commit,
                "fix_pr": fix_pr,
                "prevention_notes": prevention_notes,
                "test_added": test_added,
                "assigned_to": assigned_to,
            }
        )
        # Update error status
        return self.logs.update_status(error_id, "resolved", resolution.id)

    def wont_fix_error(
        self,
        error_id: str,
        reason: str,
    ) -> Optional[ErrorLog]:
        """Mark an error as won't fix."""
        resolution = self.resolutions.create(
            {
                "resolution_type": "wont_fix",
                "title": f"Won't fix: {reason}",
                "description": reason,
            }
        )
        return self.logs.update_status(error_id, "wont_fix", resolution.id)

    def retry_error(self, error_id: str) -> Optional[ErrorLog]:
        """Increment retry count for an error."""
        return self.logs.increment_retry(error_id)

    # -----------------------------------------------------------------------
    # Archive operations
    # -----------------------------------------------------------------------

    def archive_error(self, error_id: str) -> bool:
        """Archive an error log."""
        error = self.logs.get(error_id)
        if error:
            self.archives.archive_error(error)
            return True
        return False

    def archive_old_errors(self, older_than_days: int = 90) -> int:
        """Archive errors older than specified days. Returns count archived."""
        cutoff = datetime.utcnow() - __import__("datetime").timedelta(days=older_than_days)
        old_errors = (
            self.db.query(ErrorLog)
            .filter(ErrorLog.created_at < cutoff)
            .limit(1000)
            .all()
        )
        count = 0
        for error in old_errors:
            self.archives.archive_error(error)
            count += 1
        return count

    def cleanup_old_errors(self, retention_days: int = 365) -> int:
        """Delete errors older than retention period. Returns count deleted."""
        return self.logs.cleanup_old_errors(retention_days)

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _determine_severity(self, exc: Exception) -> str:
        """Determine error severity based on exception type."""
        critical_exceptions = (
            SystemExit,
            MemoryError,
            KeyboardInterrupt,
        )
        high_exceptions = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        medium_exceptions = (
            ValueError,
            TypeError,
            KeyError,
        )

        if isinstance(exc, critical_exceptions):
            return "critical"
        elif isinstance(exc, high_exceptions):
            return "high"
        elif isinstance(exc, medium_exceptions):
            return "medium"
        return "low"

    def _determine_status_severity(self, status_code: int) -> str:
        """Determine severity based on HTTP status code."""
        if status_code >= 500:
            return "high"
        elif status_code >= 400:
            return "medium"
        return "low"

    def _calculate_resolution_rate(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> float:
        """Calculate the resolution rate as a percentage."""
        total = self.logs.count(start=start, end=end)
        if total == 0:
            return 100.0
        resolved = self.logs.count_by_status(start=start, end=end).get("resolved", 0)
        return round((resolved / total) * 100, 2)

    def _redact_sensitive(self, data: Optional[str]) -> Optional[str]:
        """Redact sensitive fields in a JSON string."""
        if data is None:
            return None
        try:
            parsed = json.loads(data)
            sensitive = ["password", "token", "secret", "api_key", "authorization"]
            if isinstance(parsed, dict):
                parsed = {
                    k: "***" if any(s in k.lower() for s in sensitive) else v
                    for k, v in parsed.items()
                }
            return json.dumps(parsed, default=str)
        except (json.JSONDecodeError, TypeError):
            return data


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def get_error_service(db: Session) -> ErrorService:
    """Get an ErrorService instance."""
    return ErrorService(db)
