"""Error domain repositories.

Data access layer for error logs, categories, resolutions, archives, and occurrences.
Optimized for high-throughput writes and efficient querying.
"""
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, text
from sqlalchemy.orm import Session

from ..models.error import (
    ErrorArchive,
    ErrorCategory,
    ErrorLog,
    ErrorOccurrence,
    ErrorResolution,
)
from .base import BaseRepository


# ---------------------------------------------------------------------------
# ErrorLog Repository
# ---------------------------------------------------------------------------

class ErrorLogRepository(BaseRepository[ErrorLog]):
    """Repository for ErrorLog entity.

    Optimized for append-only writes and efficient time-range queries.
    """

    def __init__(self, db):
        super().__init__(ErrorLog, db)

    @staticmethod
    def _fingerprint(error_type: str, message: str, module: Optional[str] = None, line_number: Optional[int] = None) -> str:
        """Generate error fingerprint for deduplication."""
        raw = f"{error_type}:{message}:{module}:{line_number}"
        return sha256(raw.encode()).hexdigest()

    def log(
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
        browser: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        severity: str = "medium",
        environment: str = "production",
        python_version: Optional[str] = None,
        database_provider: Optional[str] = None,
        ai_provider: Optional[str] = None,
        app_version: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        category_id: Optional[str] = None,
        resume_id: Optional[str] = None,
        cover_letter_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        device_id: Optional[str] = None,
        metadata_json: Optional[str] = None,
        router: Optional[str] = None,
    ) -> ErrorLog:
        """Create an error log entry with automatic fingerprinting."""
        fingerprint = self._fingerprint(error_type, error_message, module, line_number)

        # Check if similar error exists for occurrence tracking
        existing = (
            self.db.query(ErrorLog)
            .filter(ErrorLog.error_fingerprint == fingerprint)
            .first()
        )

        if existing:
            existing.last_occurrence_at = datetime.utcnow()
            existing.occurrence_count += 1
            self.db.commit()
            self.db.refresh(existing)

            # Log individual occurrence
            occurrence = ErrorOccurrence(
                error_log_id=existing.id,
                error_fingerprint=fingerprint,
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                request_payload=request_payload,
                response_status=response_status,
                processing_time_ms=processing_time_ms,
                is_retry=existing.retry_count > 0,
                retry_attempt=existing.retry_count,
            )
            self.db.add(occurrence)
            self.db.commit()

            return existing

        return self.create(
            {
                "error_type": error_type,
                "error_message": error_message,
                "error_fingerprint": fingerprint,
                "stack_trace": stack_trace,
                "module": module,
                "function": function,
                "file_path": file_path,
                "line_number": line_number,
                "endpoint": endpoint,
                "http_method": http_method,
                "request_payload": request_payload,
                "response_status": response_status,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "browser": browser,
                "processing_time_ms": processing_time_ms,
                "severity": severity,
                "environment": environment,
                "python_version": python_version,
                "database_provider": database_provider,
                "ai_provider": ai_provider,
                "app_version": app_version,
                "user_id": user_id,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "category_id": category_id,
                "resume_id": resume_id,
                "cover_letter_id": cover_letter_id,
                "organization_id": organization_id,
                "device_id": device_id,
                "metadata_json": metadata_json,
                "router": router,
                "first_occurrence_at": datetime.utcnow(),
                "last_occurrence_at": datetime.utcnow(),
                "occurrence_count": 1,
            }
        )

    def get_by_fingerprint(self, fingerprint: str) -> Optional[ErrorLog]:
        """Get error by fingerprint."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.error_fingerprint == fingerprint)
            .first()
        )

    def get_by_entity(
        self,
        error_type: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ErrorLog]:
        """Get errors by type."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.error_type == error_type)
            .order_by(ErrorLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_user(
        self,
        user_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[ErrorLog]:
        """Get errors for a specific user."""
        query = self.db.query(ErrorLog).filter(ErrorLog.user_id == user_id)
        if status:
            query = query.filter(ErrorLog.status == status)
        return (
            query.order_by(ErrorLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_time_range(
        self,
        start: datetime,
        end: datetime,
        *,
        severity: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000,
    ) -> List[ErrorLog]:
        """Get errors within a time range."""
        query = self.db.query(ErrorLog).filter(
            ErrorLog.created_at >= start,
            ErrorLog.created_at <= end,
        )
        if severity:
            query = query.filter(ErrorLog.severity == severity)
        if environment:
            query = query.filter(ErrorLog.environment == environment)
        if status:
            query = query.filter(ErrorLog.status == status)
        return (
            query.order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_request(self, request_id: str) -> List[ErrorLog]:
        """Get all errors for a specific request."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.request_id == request_id)
            .order_by(ErrorLog.created_at.asc())
            .all()
        )

    def get_by_correlation(self, correlation_id: str) -> List[ErrorLog]:
        """Get all errors for a correlation ID."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.correlation_id == correlation_id)
            .order_by(ErrorLog.created_at.asc())
            .all()
        )

    def get_by_severity(
        self,
        severity: str,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[ErrorLog]:
        """Get errors by severity."""
        query = self.db.query(ErrorLog).filter(ErrorLog.severity == severity)
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        return (
            query.order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        status: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ErrorLog]:
        """Get errors by status."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.status == status)
            .order_by(ErrorLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self,
        category_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ErrorLog]:
        """Get errors by category."""
        return (
            self.db.query(ErrorLog)
            .filter(ErrorLog.category_id == category_id)
            .order_by(ErrorLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_unresolved(
        self,
        *,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[ErrorLog]:
        """Get unresolved errors."""
        query = self.db.query(ErrorLog).filter(
            ErrorLog.status.in_(["new", "acknowledged", "investigating"])
        )
        if severity:
            query = query.filter(ErrorLog.severity == severity)
        return (
            query.order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_critical_errors(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[ErrorLog]:
        """Get critical errors."""
        return self.get_by_severity("critical", start=start, end=end, limit=limit)

    def get_recent(self, limit: int = 50) -> List[ErrorLog]:
        """Get most recent errors."""
        return (
            self.db.query(ErrorLog)
            .order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_by_severity(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Count errors by severity."""
        query = self.db.query(
            ErrorLog.severity,
            func.count(ErrorLog.id).label("count"),
        )
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        results = query.group_by(ErrorLog.severity).all()
        return {r.severity: r.count for r in results}

    def count_by_status(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Count errors by status."""
        query = self.db.query(
            ErrorLog.status,
            func.count(ErrorLog.id).label("count"),
        )
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        results = query.group_by(ErrorLog.status).all()
        return {r.status: r.count for r in results}

    def count_by_type(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top error types with counts."""
        query = self.db.query(
            ErrorLog.error_type,
            func.count(ErrorLog.id).label("count"),
        )
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        results = (
            query.group_by(ErrorLog.error_type)
            .order_by(func.count(ErrorLog.id).desc())
            .limit(limit)
            .all()
        )
        return [{"error_type": r.error_type, "count": r.count} for r in results]

    def get_statistics(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        # Build base query for total count
        query = self.db.query(ErrorLog)
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        total_count = query.count()

        return {
            "total_count": total_count,
            "by_severity": self.count_by_severity(start=start, end=end),
            "by_status": self.count_by_status(start=start, end=end),
            "top_types": self.count_by_type(start=start, end=end, limit=10),
        }

    def update_status(
        self,
        error_id: str,
        status: str,
        resolution_id: Optional[str] = None,
    ) -> Optional[ErrorLog]:
        """Update error status."""
        error = self.get(error_id)
        if error:
            error.status = status
            if resolution_id:
                error.resolution_id = resolution_id
            self.db.commit()
            self.db.refresh(error)
        return error

    def increment_retry(self, error_id: str) -> Optional[ErrorLog]:
        """Increment retry count for an error."""
        error = self.get(error_id)
        if error:
            error.retry_count += 1
            self.db.commit()
            self.db.refresh(error)
        return error

    def count(self, *, start: Optional[datetime] = None, end: Optional[datetime] = None, **kwargs) -> int:
        """Count errors with optional time range."""
        query = self.db.query(ErrorLog)
        if start:
            query = query.filter(ErrorLog.created_at >= start)
        if end:
            query = query.filter(ErrorLog.created_at <= end)
        return query.count()

    def cleanup_old_errors(self, retention_days: int = 90) -> int:
        """Delete errors older than retention period. Returns count deleted."""
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        count = (
            self.db.query(ErrorLog)
            .filter(ErrorLog.created_at < cutoff)
            .delete()
        )
        self.db.commit()
        return count


# ---------------------------------------------------------------------------
# ErrorCategory Repository
# ---------------------------------------------------------------------------

class ErrorCategoryRepository(BaseRepository[ErrorCategory]):
    """Repository for ErrorCategory entity."""

    def __init__(self, db):
        super().__init__(ErrorCategory, db)

    def get_by_name(self, name: str) -> Optional[ErrorCategory]:
        """Get category by name."""
        return (
            self.db.query(ErrorCategory)
            .filter(ErrorCategory.name == name)
            .first()
        )

    def get_active_categories(self) -> List[ErrorCategory]:
        """Get all active categories."""
        return (
            self.db.query(ErrorCategory)
            .filter(ErrorCategory.is_active == True)
            .all()
        )

    def auto_categorize(self, error_type: str, message: str) -> Optional[ErrorCategory]:
        """Attempt to auto-categorize an error based on patterns."""
        import json
        import re
        categories = self.get_active_categories()
        for category in categories:
            if category.patterns:
                try:
                    patterns = json.loads(category.patterns)
                    for pattern in patterns:
                        if re.search(pattern, f"{error_type}: {message}", re.IGNORECASE):
                            return category
                except (json.JSONDecodeError, TypeError):
                    continue
        return None


# ---------------------------------------------------------------------------
# ErrorResolution Repository
# ---------------------------------------------------------------------------

class ErrorResolutionRepository(BaseRepository[ErrorResolution]):
    """Repository for ErrorResolution entity."""

    def __init__(self, db):
        super().__init__(ErrorResolution, db)

    def get_by_type(
        self,
        resolution_type: str,
        *,
        limit: int = 100,
    ) -> List[ErrorResolution]:
        """Get resolutions by type."""
        return (
            self.db.query(ErrorResolution)
            .filter(ErrorResolution.resolution_type == resolution_type)
            .order_by(ErrorResolution.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_assignee(
        self,
        assigned_to: str,
        *,
        limit: int = 100,
    ) -> List[ErrorResolution]:
        """Get resolutions assigned to a user."""
        return (
            self.db.query(ErrorResolution)
            .filter(ErrorResolution.assigned_to == assigned_to)
            .order_by(ErrorResolution.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_unverified(self, limit: int = 100) -> List[ErrorResolution]:
        """Get unverified resolutions."""
        return (
            self.db.query(ErrorResolution)
            .filter(ErrorResolution.is_verified == False)
            .order_by(ErrorResolution.created_at.desc())
            .limit(limit)
            .all()
        )

    def verify_resolution(
        self,
        resolution_id: str,
        verified_by: str,
    ) -> Optional[ErrorResolution]:
        """Mark a resolution as verified."""
        resolution = self.get(resolution_id)
        if resolution:
            resolution.is_verified = True
            resolution.verified_at = datetime.utcnow()
            resolution.verified_by = verified_by
            self.db.commit()
            self.db.refresh(resolution)
        return resolution


# ---------------------------------------------------------------------------
# ErrorOccurrence Repository
# ---------------------------------------------------------------------------

class ErrorOccurrenceRepository(BaseRepository[ErrorOccurrence]):
    """Repository for ErrorOccurrence entity."""

    def __init__(self, db):
        super().__init__(ErrorOccurrence, db)

    def get_by_error_log(self, error_log_id: str, limit: int = 100) -> List[ErrorOccurrence]:
        """Get occurrences for an error log."""
        return (
            self.db.query(ErrorOccurrence)
            .filter(ErrorOccurrence.error_log_id == error_log_id)
            .order_by(ErrorOccurrence.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_fingerprint(
        self,
        fingerprint: str,
        *,
        limit: int = 100,
    ) -> List[ErrorOccurrence]:
        """Get occurrences by fingerprint."""
        return (
            self.db.query(ErrorOccurrence)
            .filter(ErrorOccurrence.error_fingerprint == fingerprint)
            .order_by(ErrorOccurrence.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_occurrences(
        self,
        error_log_id: str,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> int:
        """Count occurrences for an error."""
        query = self.db.query(func.count(ErrorOccurrence.id)).filter(
            ErrorOccurrence.error_log_id == error_log_id
        )
        if start:
            query = query.filter(ErrorOccurrence.created_at >= start)
        if end:
            query = query.filter(ErrorOccurrence.created_at <= end)
        return query.scalar()


# ---------------------------------------------------------------------------
# ErrorArchive Repository
# ---------------------------------------------------------------------------

class ErrorArchiveRepository(BaseRepository[ErrorArchive]):
    """Repository for ErrorArchive entity."""

    def __init__(self, db):
        super().__init__(ErrorArchive, db)

    def archive_error(self, error_log: ErrorLog) -> ErrorArchive:
        """Archive an error log entry."""
        archive = ErrorArchive(
            original_id=error_log.id,
            user_id=error_log.user_id,
            session_id=error_log.session_id,
            request_id=error_log.request_id,
            correlation_id=error_log.correlation_id,
            error_type=error_log.error_type,
            error_message=error_log.error_message,
            error_fingerprint=error_log.error_fingerprint,
            module=error_log.module,
            function=error_log.function,
            file_path=error_log.file_path,
            line_number=error_log.line_number,
            stack_trace=error_log.stack_trace,
            endpoint=error_log.endpoint,
            http_method=error_log.http_method,
            request_payload=error_log.request_payload,
            ip_address=error_log.ip_address,
            user_agent=error_log.user_agent,
            browser=error_log.browser,
            response_status=error_log.response_status,
            processing_time_ms=error_log.processing_time_ms,
            severity=error_log.severity,
            environment=error_log.environment,
            python_version=error_log.python_version,
            database_provider=error_log.database_provider,
            ai_provider=error_log.ai_provider,
            app_version=error_log.app_version,
            retry_count=error_log.retry_count,
            status=error_log.status,
            resolution_id=error_log.resolution_id,
            category_id=error_log.category_id,
            resume_id=error_log.resume_id,
            cover_letter_id=error_log.cover_letter_id,
            organization_id=error_log.organization_id,
            device_id=error_log.device_id,
            first_occurrence_at=error_log.first_occurrence_at,
            last_occurrence_at=error_log.last_occurrence_at,
            occurrence_count=error_log.occurrence_count,
            metadata_json=error_log.metadata_json,
            created_at=error_log.created_at,
            archived_at=datetime.utcnow(),
        )
        self.db.add(archive)
        self.db.commit()
        self.db.refresh(archive)
        return archive

    def get_by_original_id(self, original_id: str) -> Optional[ErrorArchive]:
        """Get archived error by original error log ID."""
        return (
            self.db.query(ErrorArchive)
            .filter(ErrorArchive.original_id == original_id)
            .first()
        )


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def get_error_repositories(db: Session) -> Dict[str, Any]:
    """Get all error repositories for a database session."""
    return {
        "error_logs": ErrorLogRepository(db),
        "error_categories": ErrorCategoryRepository(db),
        "error_resolutions": ErrorResolutionRepository(db),
        "error_occurrences": ErrorOccurrenceRepository(db),
        "error_archives": ErrorArchiveRepository(db),
    }
