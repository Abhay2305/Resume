"""Audit domain service.

Provides high-level audit logging operations. Handles sensitive data
redaction, state diff computation, and integration with the repository layer.

This is the centralized audit framework for the entire PROCS platform.
Every module should use this service instead of implementing custom audit logic.

Public API:
    log_create()        — Log entity creation
    log_update()        — Log entity update
    log_delete()        — Log entity deletion
    log_login()         — Log authentication login
    log_logout()        — Log authentication logout
    log_security_event() — Log security events (access denied, suspicious activity)
    log_system_event()  — Log system events (startup, shutdown, config change)
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..context import get_request_id, get_user_id, get_endpoint, get_http_method
from ..models.audit import AuditLog
from ..repositories.audit import (
    AuditArchiveRepository,
    AuditConfigRepository,
    AuditExportRepository,
    AuditLogRepository,
)

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging operations.

    Public API follows PROC-SPEC-0.4. Business modules should only provide
    business-specific data (entity_type, entity_id, old/new values). All
    request context (request_id, user_id, endpoint, http_method) is resolved
    automatically from contextvars.

    Usage:
        service = AuditService(db)
        service.log_create(entity_type="Resume", entity_id="456", new_state={...})
        service.log_update(entity_type="Resume", entity_id="456", previous_state={...}, new_state={...})
    """

    def __init__(self, db: Session):
        self.db = db
        self.logs = AuditLogRepository(db)
        self.configs = AuditConfigRepository(db)
        self.archives = AuditArchiveRepository(db)
        self.exports = AuditExportRepository(db)

    # -------------------------------------------------------------------
    # Public API — PROC-SPEC-0.4
    # -------------------------------------------------------------------

    def log_create(
        self,
        *,
        entity_type: str,
        entity_id: str,
        new_state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a create action on an entity."""
        return self._write_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action="create",
            description=description or f"Created {entity_type}",
            new_state=new_state,
            tags=tags,
        )

    def log_update(
        self,
        *,
        entity_type: str,
        entity_id: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log an update action on an entity."""
        return self._write_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action="update",
            description=description or f"Updated {entity_type}",
            previous_state=previous_state,
            new_state=new_state,
            tags=tags,
        )

    def log_delete(
        self,
        *,
        entity_type: str,
        entity_id: str,
        previous_state: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a delete action on an entity."""
        return self._write_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action="delete",
            description=description or f"Deleted {entity_type}",
            previous_state=previous_state,
            tags=tags,
        )

    def log_login(
        self,
        *,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata_json: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a login event."""
        action = "login" if success else "login_failed"
        status = "SUCCESS" if success else "FAILURE"
        return self._write_event(
            entity_type="admin_auth",
            entity_id=user_id,
            action=action,
            description=f"Admin login {status}",
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=200 if success else 401,
            error_message=error_message,
            metadata_json=metadata_json,
            tags=status,
            override_user_id=user_id,
        )

    def log_logout(
        self,
        *,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a logout event."""
        return self._write_event(
            entity_type="admin_auth",
            entity_id=user_id,
            action="logout",
            description="Admin logout",
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=200,
            tags="SUCCESS",
            override_user_id=user_id,
        )

    def log_security_event(
        self,
        *,
        action: str,
        description: str,
        user_id: Optional[str] = None,
        entity_type: str = "admin_auth",
        entity_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = False,
        error_message: Optional[str] = None,
        metadata_json: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a security event (access denied, suspicious activity, etc.)."""
        status = "SUCCESS" if success else "FAILURE"
        return self._write_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=200 if success else 403,
            error_message=error_message,
            metadata_json=metadata_json,
            tags=status,
            override_user_id=user_id,
        )

    def log_system_event(
        self,
        *,
        action: str,
        description: str,
        entity_type: str = "system",
        entity_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata_json: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log a system event (startup, shutdown, config change, etc.)."""
        status = "SUCCESS" if success else "FAILURE"
        return self._write_event(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            response_status=200 if success else 500,
            error_message=error_message,
            metadata_json=metadata_json,
            tags=status,
        )

    # -------------------------------------------------------------------
    # Query API
    # -------------------------------------------------------------------

    def search_logs(
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
        return self.logs.search(
            page=page,
            limit=limit,
            entity_type=entity_type,
            action=action,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            search=search,
        )

    def get_entity_history(
        self, entity_type: str, entity_id: str, limit: int = 100
    ) -> List[AuditLog]:
        """Get full audit history for an entity."""
        return self.logs.get_by_entity(entity_type, entity_id, limit)

    def get_user_history(
        self,
        user_id: str,
        *,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        """Get audit history for a user."""
        return self.logs.get_by_user(user_id, limit=limit, offset=offset, action=action)

    def get_request_logs(self, request_id: str) -> List[AuditLog]:
        """Get all logs for a specific request."""
        return self.logs.get_by_request(request_id)

    def get_correlation_logs(self, correlation_id: str) -> List[AuditLog]:
        """Get all logs for a correlation ID."""
        return self.logs.get_by_correlation(correlation_id)

    def get_errors(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get error logs."""
        return self.logs.get_errors(start=start, end=end, limit=limit)

    def get_slow_requests(
        self,
        threshold_ms: int = 1000,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get slow request logs."""
        return self.logs.get_slow_requests(
            threshold_ms, start=start, end=end, limit=limit
        )

    def get_recent(self, limit: int = 50) -> List[AuditLog]:
        """Get most recent audit logs."""
        return self.logs.get_recent(limit)

    def get_summary(
        self,
        *,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get audit summary with action and entity counts."""
        return {
            "action_summary": self.logs.get_action_summary(start=start, end=end),
            "entity_summary": self.logs.get_entity_summary(start=start, end=end),
            "total_errors": len(self.logs.get_errors(start=start, end=end, limit=0)),
        }

    # -------------------------------------------------------------------
    # State diff helpers
    # -------------------------------------------------------------------

    @staticmethod
    def compute_diff(
        old_state: Optional[Dict[str, Any]],
        new_state: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compute the diff between old and new state."""
        if not old_state and not new_state:
            return {}
        if not old_state:
            return {"added": list(new_state.keys())}
        if not new_state:
            return {"removed": list(old_state.keys())}

        added = set(new_state.keys()) - set(old_state.keys())
        removed = set(old_state.keys()) - set(new_state.keys())
        changed = {
            k for k in set(old_state.keys()) & set(new_state.keys())
            if old_state[k] != new_state[k]
        }

        diff = {}
        if added:
            diff["added"] = list(added)
        if removed:
            diff["removed"] = list(removed)
        if changed:
            diff["changed"] = {
                k: {"old": old_state[k], "new": new_state[k]} for k in changed
            }
        return diff

    # -------------------------------------------------------------------
    # Private implementation
    # -------------------------------------------------------------------

    def _write_event(
        self,
        *,
        entity_type: str,
        entity_id: Optional[str] = None,
        action: str,
        description: Optional[str] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        metadata_json: Optional[str] = None,
        tags: Optional[str] = None,
        override_user_id: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Shared write implementation. All public methods delegate here.

        Resolves request_id, user_id, endpoint, and http_method from
        contextvars automatically. Business callers only provide
        business-specific data.
        """
        try:
            if not self._should_audit(entity_type, action):
                return None

            request_id = get_request_id()
            user_id = override_user_id or get_user_id()
            endpoint = get_endpoint()
            http_method = get_http_method()

            return self.logs.log(
                user_id=user_id,
                request_id=request_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                description=description,
                previous_state=self._serialize_state(previous_state, entity_type),
                new_state=self._serialize_state(new_state, entity_type),
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method,
                response_status=response_status,
                error_message=error_message,
                processing_time_ms=processing_time_ms,
                metadata_json=metadata_json,
                tags=tags,
            )
        except Exception as e:
            # Never let audit logging break business operations
            logger.warning("Audit _write_event failed: %s", e)
            return None

    def _should_audit(self, entity_type: str, action: str) -> bool:
        """Check if this entity type and action should be audited."""
        return self.configs.is_audited(entity_type, action)

    def _serialize_state(
        self, state: Optional[Dict[str, Any]], entity_type: str
    ) -> Optional[str]:
        """Serialize state with sensitive field redaction."""
        if state is None:
            return None
        sensitive = self.configs.get_sensitive_fields(entity_type)
        redacted = {k: "***" if k in sensitive else v for k, v in state.items()}
        return json.dumps(redacted, default=str)

    def _redact_sensitive(
        self, data: Optional[str], entity_type: str
    ) -> Optional[str]:
        """Redact sensitive fields in a JSON string."""
        if data is None:
            return None
        try:
            parsed = json.loads(data)
            sensitive = self.configs.get_sensitive_fields(entity_type)
            if sensitive and isinstance(parsed, dict):
                parsed = {k: "***" if k in sensitive else v for k, v in parsed.items()}
            return json.dumps(parsed, default=str)
        except (json.JSONDecodeError, TypeError):
            return data

    def _log_request(
        self,
        *,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: str,
        http_method: str,
        response_status: int,
        processing_time_ms: Optional[int] = None,
        request_body: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Log an HTTP request. Called by AuditMiddleware (internal infrastructure).

        Bypasses _should_audit() because HTTP request logging is always-on
        infrastructure, not governed by entity-level audit configs.
        """
        try:
            return self.logs.log(
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                correlation_id=correlation_id,
                entity_type="http_request",
                action=f"{http_method.lower()}:{endpoint}",
                description=f"{http_method} {endpoint} -> {response_status}",
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method,
                response_status=response_status,
                request_body=self._redact_sensitive(request_body, "http_request"),
                error_message=error_message,
                processing_time_ms=processing_time_ms,
            )
        except Exception as e:
            logger.warning("Audit _log_request failed: %s", e)
            return None


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def get_audit_service(db: Session) -> AuditService:
    """Get an AuditService instance."""
    return AuditService(db)
