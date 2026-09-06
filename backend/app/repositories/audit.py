"""Audit domain repositories.

Data access layer for audit logs, configurations, archives, and exports.
Optimized for high-throughput writes and efficient querying.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, text
from sqlalchemy.orm import Session

from ..models.audit import AuditArchive, AuditConfig, AuditExport, AuditLog
from .base import BaseRepository


# ---------------------------------------------------------------------------
# AuditLog Repository
# ---------------------------------------------------------------------------

class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog entity.

    Optimized for append-only writes and efficient time-range queries.
    """

    def __init__(self, db):
        super().__init__(AuditLog, db)

    def log(
        self,
        *,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        entity_type: str,
        entity_id: Optional[str] = None,
        action: str,
        description: Optional[str] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        request_body: Optional[str] = None,
        response_status: Optional[int] = None,
        response_body_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        metadata_json: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        return self.create(
            {
                "user_id": user_id,
                "session_id": session_id,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": action,
                "description": description,
                "previous_state": previous_state,
                "new_state": new_state,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "endpoint": endpoint,
                "http_method": http_method,
                "request_body": request_body,
                "response_status": response_status,
                "response_body_summary": response_body_summary,
                "error_message": error_message,
                "processing_time_ms": processing_time_ms,
                "metadata_json": metadata_json,
                "tags": tags,
            }
        )

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get all audit logs for a specific entity."""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_user(
        self,
        user_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        return (
            query.order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_time_range(
        self,
        start: datetime,
        end: datetime,
        *,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 1000,
    ) -> List[AuditLog]:
        """Get audit logs within a time range."""
        query = self.db.query(AuditLog).filter(
            AuditLog.created_at >= start,
            AuditLog.created_at <= end,
        )
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action:
            query = query.filter(AuditLog.action == action)
        return (
            query.order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_request(self, request_id: str) -> List[AuditLog]:
        """Get all audit logs for a specific request."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.request_id == request_id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )

    def get_by_correlation(self, correlation_id: str) -> List[AuditLog]:
        """Get all audit logs for a correlation ID (distributed tracing)."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.correlation_id == correlation_id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )

    def get_errors(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs with errors."""
        query = self.db.query(AuditLog).filter(
            AuditLog.response_status >= 400
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        return (
            query.order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_slow_requests(
        self,
        threshold_ms: int = 1000,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs for slow requests."""
        query = self.db.query(AuditLog).filter(
            AuditLog.processing_time_ms >= threshold_ms
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        return (
            query.order_by(AuditLog.processing_time_ms.desc())
            .limit(limit)
            .all()
        )

    def get_recent(self, limit: int = 50) -> List[AuditLog]:
        """Get most recent audit logs."""
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def count_by_user(
        self,
        user_id: str,
        *,
        action: Optional[str] = None,
    ) -> int:
        """Count audit logs for a specific user."""
        query = self.db.query(func.count(AuditLog.id)).filter(
            AuditLog.user_id == user_id
        )
        if action:
            query = query.filter(AuditLog.action == action)
        return query.scalar()

    def count_by_entity(
        self,
        entity_type: str,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> int:
        """Count audit logs for an entity type."""
        query = self.db.query(func.count(AuditLog.id)).filter(
            AuditLog.entity_type == entity_type
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        return query.scalar()

    def count_by_action(
        self,
        action: str,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> int:
        """Count audit logs for an action."""
        query = self.db.query(func.count(AuditLog.id)).filter(
            AuditLog.action == action
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        return query.scalar()

    def get_action_summary(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get summary of actions with counts."""
        query = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id).label("count"),
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        results = (
            query.group_by(AuditLog.action)
            .order_by(func.count(AuditLog.id).desc())
            .limit(limit)
            .all()
        )
        return [{"action": r.action, "count": r.count} for r in results]

    def get_entity_summary(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get summary of entity types with counts."""
        query = self.db.query(
            AuditLog.entity_type,
            func.count(AuditLog.id).label("count"),
        )
        if start:
            query = query.filter(AuditLog.created_at >= start)
        if end:
            query = query.filter(AuditLog.created_at <= end)
        results = (
            query.group_by(AuditLog.entity_type)
            .order_by(func.count(AuditLog.id).desc())
            .limit(limit)
            .all()
        )
        return [{"entity_type": r.entity_type, "count": r.count} for r in results]

    def search(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search audit logs with filters and pagination."""
        query = self.db.query(AuditLog)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        if search:
            query = query.filter(AuditLog.description.ilike(f"%{search}%"))

        total = query.count()
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        offset = (page - 1) * limit
        items = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": total_pages,
        }

    def cleanup_old_logs(self, retention_days: int = 365) -> int:
        """Delete audit logs older than retention period. Returns count deleted."""
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        count = (
            self.db.query(AuditLog)
            .filter(AuditLog.created_at < cutoff)
            .delete()
        )
        self.db.commit()
        return count


# ---------------------------------------------------------------------------
# AuditConfig Repository
# ---------------------------------------------------------------------------

class AuditConfigRepository(BaseRepository[AuditConfig]):
    """Repository for AuditConfig entity."""

    def __init__(self, db):
        super().__init__(AuditConfig, db)

    def get_by_entity(self, entity_type: str) -> Optional[AuditConfig]:
        """Get audit configuration for an entity type."""
        return (
            self.db.query(AuditConfig)
            .filter(AuditConfig.entity_type == entity_type)
            .first()
        )

    def get_enabled_configs(self) -> List[AuditConfig]:
        """Get all enabled audit configurations."""
        return (
            self.db.query(AuditConfig)
            .filter(AuditConfig.is_enabled == True)
            .all()
        )

    def is_audited(self, entity_type: str, action: str) -> bool:
        """Check if an entity type and action should be audited."""
        config = self.get_by_entity(entity_type)
        if not config or not config.is_enabled:
            return False
        action_attr = f"audit_{action}"
        return getattr(config, action_attr, False)

    def get_retention_days(self, entity_type: str) -> int:
        """Get retention period for an entity type."""
        config = self.get_by_entity(entity_type)
        return config.retention_days if config else 365

    def get_sensitive_fields(self, entity_type: str) -> List[str]:
        """Get sensitive fields to redact for an entity type."""
        import json
        config = self.get_by_entity(entity_type)
        if config and config.sensitive_fields:
            try:
                return json.loads(config.sensitive_fields)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def create_default_config(self, entity_type: str) -> AuditConfig:
        """Create a default audit configuration for an entity type."""
        return self.create(
            {
                "entity_type": entity_type,
                "is_enabled": True,
                "audit_create": True,
                "audit_read": False,
                "audit_update": True,
                "audit_delete": True,
                "retention_days": 365,
                "archive_after_days": 90,
                "sample_rate": 100,
            }
        )


# ---------------------------------------------------------------------------
# AuditArchive Repository
# ---------------------------------------------------------------------------

class AuditArchiveRepository(BaseRepository[AuditArchive]):
    """Repository for AuditArchive entity."""

    def __init__(self, db):
        super().__init__(AuditArchive, db)

    def archive_log(self, log: AuditLog) -> AuditArchive:
        """Archive an audit log entry."""
        archive = AuditArchive(
            original_id=log.id,
            user_id=log.user_id,
            session_id=log.session_id,
            request_id=log.request_id,
            correlation_id=log.correlation_id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            description=log.description,
            previous_state=log.previous_state,
            new_state=log.new_state,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            endpoint=log.endpoint,
            http_method=log.http_method,
            request_body=log.request_body,
            response_status=log.response_status,
            response_body_summary=log.response_body_summary,
            error_message=log.error_message,
            processing_time_ms=log.processing_time_ms,
            metadata_json=log.metadata_json,
            tags=log.tags,
            created_at=log.created_at,
            archived_at=datetime.utcnow(),
        )
        self.db.add(archive)
        self.db.commit()
        self.db.refresh(archive)
        return archive

    def get_by_original_id(self, original_id: str) -> Optional[AuditArchive]:
        """Get archived log by original audit log ID."""
        return (
            self.db.query(AuditArchive)
            .filter(AuditArchive.original_id == original_id)
            .first()
        )

    def get_archived_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100,
    ) -> List[AuditArchive]:
        """Get archived logs for a specific entity."""
        return (
            self.db.query(AuditArchive)
            .filter(
                AuditArchive.entity_type == entity_type,
                AuditArchive.entity_id == entity_id,
            )
            .order_by(AuditArchive.created_at.desc())
            .limit(limit)
            .all()
        )


# ---------------------------------------------------------------------------
# AuditExport Repository
# ---------------------------------------------------------------------------

class AuditExportRepository(BaseRepository[AuditExport]):
    """Repository for AuditExport entity."""

    def __init__(self, db):
        super().__init__(AuditExport, db)

    def create_export_job(
        self,
        requested_by: str,
        *,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filters_json: Optional[str] = None,
    ) -> AuditExport:
        """Create a new export job."""
        return self.create(
            {
                "requested_by": requested_by,
                "entity_type": entity_type,
                "start_date": start_date,
                "end_date": end_date,
                "filters_json": filters_json,
                "status": "pending",
            }
        )

    def get_pending_exports(self) -> List[AuditExport]:
        """Get all pending export jobs."""
        return (
            self.db.query(AuditExport)
            .filter(AuditExport.status == "pending")
            .order_by(AuditExport.created_at.asc())
            .all()
        )

    def complete_export(
        self,
        export_id: str,
        file_path: str,
        file_size_bytes: int,
        record_count: int,
    ) -> AuditExport:
        """Mark an export job as completed."""
        export = self.get(export_id)
        if export:
            export.status = "completed"
            export.file_path = file_path
            export.file_size_bytes = file_size_bytes
            export.record_count = record_count
            export.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(export)
        return export

    def fail_export(self, export_id: str, error_message: str) -> AuditExport:
        """Mark an export job as failed."""
        export = self.get(export_id)
        if export:
            export.status = "failed"
            export.error_message = error_message
            export.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(export)
        return export


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def get_audit_repositories(db: Session) -> Dict[str, Any]:
    """Get all audit repositories for a database session."""
    return {
        "audit_logs": AuditLogRepository(db),
        "audit_configs": AuditConfigRepository(db),
        "audit_archives": AuditArchiveRepository(db),
        "audit_exports": AuditExportRepository(db),
    }
