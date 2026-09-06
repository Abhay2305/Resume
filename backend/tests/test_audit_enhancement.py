"""Tests for Audit System Enhancement (PROC-SPEC-0.4).

Comprehensive tests covering:
- AuditService public API (log_create, log_update, log_delete, log_login, log_logout, log_security_event, log_system_event)
- Auto-resolution of request_id, user_id, endpoint, http_method from context
- Failure isolation (audit errors never block business operations)
- Sensitive data redaction
- Audit config lookup (should_audit logic)
- Seed data for PROCS entities
- Context integration
"""
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

from app.context import (
    set_request_id, set_user_id, set_endpoint, set_http_method,
    get_request_id, get_user_id, get_endpoint, get_http_method,
    clear_context,
)
from app.services.audit_service import AuditService
from app.models.audit import AuditLog


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_context():
    """Ensure context is clean before and after each test."""
    clear_context()
    yield
    clear_context()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_audit_service(mock_db):
    """Create an AuditService with mocked repositories."""
    service = AuditService(mock_db)
    # Mock the config to always allow auditing
    service.configs.is_audited = MagicMock(return_value=True)
    service.configs.get_sensitive_fields = MagicMock(return_value=["password", "token"])
    return service


# ---------------------------------------------------------------------------
# Test Class: Context Auto-Resolution
# ---------------------------------------------------------------------------

class TestContextAutoResolution:
    """Tests that AuditService resolves context variables automatically."""

    def test_request_id_resolved_from_context(self, mock_audit_service):
        """log_create should use request_id from context."""
        set_request_id("req-ctx-123")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"name": "test"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["request_id"] == "req-ctx-123"

    def test_user_id_resolved_from_context(self, mock_audit_service):
        """log_create should use user_id from context when not overridden."""
        set_user_id("user-ctx-456")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"name": "test"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["user_id"] == "user-ctx-456"

    def test_endpoint_resolved_from_context(self, mock_audit_service):
        """log_create should use endpoint from context."""
        set_endpoint("/api/procs/users/123")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"name": "test"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["endpoint"] == "/api/procs/users/123"

    def test_http_method_resolved_from_context(self, mock_audit_service):
        """log_create should use http_method from context."""
        set_http_method("PUT")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"name": "test"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["http_method"] == "PUT"

    def test_all_context_resolved_together(self, mock_audit_service):
        """All context variables should be resolved simultaneously."""
        set_request_id("req-all-789")
        set_user_id("user-all-789")
        set_endpoint("/api/procs/resumes/abc")
        set_http_method("DELETE")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_delete(
            entity_type="admin_resume",
            entity_id="resume-abc",
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["request_id"] == "req-all-789"
        assert call_kwargs["user_id"] == "user-all-789"
        assert call_kwargs["endpoint"] == "/api/procs/resumes/abc"
        assert call_kwargs["http_method"] == "DELETE"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_create
# ---------------------------------------------------------------------------

class TestLogCreate:
    """Tests for AuditService.log_create()."""

    def test_log_create_writes_to_repository(self, mock_audit_service):
        """log_create should call logs.log with correct action."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"email": "test@example.com"},
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["entity_type"] == "admin_user"
        assert call_kwargs["entity_id"] == "user-1"
        assert call_kwargs["action"] == "create"

    def test_log_create_serializes_new_state(self, mock_audit_service):
        """log_create should serialize new_state with redaction."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"email": "test@example.com", "password": "secret123"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        new_state = json.loads(call_kwargs["new_state"])
        assert new_state["email"] == "test@example.com"
        assert new_state["password"] == "***"

    def test_log_create_returns_none_when_disabled(self, mock_audit_service):
        """log_create should return None when auditing is disabled for entity."""
        mock_audit_service.configs.is_audited = MagicMock(return_value=False)
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
        )

        assert result is None
        mock_audit_service.logs.log.assert_not_called()

    def test_log_create_exception_does_not_propagate(self, mock_audit_service):
        """log_create should catch exceptions and return None."""
        mock_audit_service.configs.is_audited = MagicMock(side_effect=Exception("db error"))

        result = mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
        )

        assert result is None


# ---------------------------------------------------------------------------
# Test Class: Public API — log_update
# ---------------------------------------------------------------------------

class TestLogUpdate:
    """Tests for AuditService.log_update()."""

    def test_log_update_writes_to_repository(self, mock_audit_service):
        """log_update should call logs.log with correct action."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_update(
            entity_type="admin_resume",
            entity_id="resume-1",
            previous_state={"title": "Old Title"},
            new_state={"title": "New Title"},
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "update"
        assert call_kwargs["entity_type"] == "admin_resume"

    def test_log_update_serializes_both_states(self, mock_audit_service):
        """log_update should serialize both previous and new state."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_update(
            entity_type="admin_user",
            entity_id="resume-1",
            previous_state={"title": "Old", "password": "abc"},
            new_state={"title": "New", "password": "xyz"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        prev = json.loads(call_kwargs["previous_state"])
        new = json.loads(call_kwargs["new_state"])
        assert prev["title"] == "Old"
        assert prev["password"] == "***"
        assert new["title"] == "New"
        assert new["password"] == "***"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_delete
# ---------------------------------------------------------------------------

class TestLogDelete:
    """Tests for AuditService.log_delete()."""

    def test_log_delete_writes_to_repository(self, mock_audit_service):
        """log_delete should call logs.log with correct action."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_delete(
            entity_type="admin_user",
            entity_id="user-1",
            previous_state={"email": "deleted@example.com"},
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "delete"
        assert call_kwargs["entity_id"] == "user-1"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_login
# ---------------------------------------------------------------------------

class TestLogLogin:
    """Tests for AuditService.log_login()."""

    def test_log_login_success(self, mock_audit_service):
        """log_login with success=True should write login event."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_login(
            user_id="admin-1",
            success=True,
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0",
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "login"
        assert call_kwargs["entity_type"] == "admin_auth"
        assert call_kwargs["tags"] == "SUCCESS"
        assert call_kwargs["response_status"] == 200

    def test_log_login_failure(self, mock_audit_service):
        """log_login with success=False should write login_failed event."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_login(
            user_id="admin-1",
            success=False,
            error_message="Invalid credentials",
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "login_failed"
        assert call_kwargs["tags"] == "FAILURE"
        assert call_kwargs["response_status"] == 401
        assert call_kwargs["error_message"] == "Invalid credentials"

    def test_log_login_uses_override_user_id(self, mock_audit_service):
        """log_login should use explicit user_id over context user_id."""
        set_user_id("context-user")
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_login(user_id="explicit-admin", success=True)

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["user_id"] == "explicit-admin"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_logout
# ---------------------------------------------------------------------------

class TestLogLogout:
    """Tests for AuditService.log_logout()."""

    def test_log_logout_writes_to_repository(self, mock_audit_service):
        """log_logout should write logout event."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_logout(
            user_id="admin-1",
            ip_address="127.0.0.1",
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "logout"
        assert call_kwargs["entity_type"] == "admin_auth"
        assert call_kwargs["tags"] == "SUCCESS"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_security_event
# ---------------------------------------------------------------------------

class TestLogSecurityEvent:
    """Tests for AuditService.log_security_event()."""

    def test_log_security_event_access_denied(self, mock_audit_service):
        """log_security_event should write access denied event."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_security_event(
            action="access_denied",
            description="Non-admin user attempted admin access",
            user_id="user-1",
            entity_type="admin_auth",
            entity_id="user-1",
            success=False,
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "access_denied"
        assert call_kwargs["tags"] == "FAILURE"
        assert call_kwargs["response_status"] == 403

    def test_log_security_event_default_entity_type(self, mock_audit_service):
        """log_security_event should default entity_type to admin_auth."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_security_event(
            action="suspicious_activity",
            description="Multiple failed logins",
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["entity_type"] == "admin_auth"


# ---------------------------------------------------------------------------
# Test Class: Public API — log_system_event
# ---------------------------------------------------------------------------

class TestLogSystemEvent:
    """Tests for AuditService.log_system_event()."""

    def test_log_system_event_success(self, mock_audit_service):
        """log_system_event should write system event."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        result = mock_audit_service.log_system_event(
            action="startup",
            description="Application started",
            success=True,
        )

        assert result is not None
        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["action"] == "startup"
        assert call_kwargs["entity_type"] == "system"
        assert call_kwargs["tags"] == "SUCCESS"

    def test_log_system_event_failure(self, mock_audit_service):
        """log_system_event with success=False should set 500 status."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_system_event(
            action="config_change",
            description="Failed to apply config",
            success=False,
            error_message="Config file not found",
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        assert call_kwargs["response_status"] == 500
        assert call_kwargs["tags"] == "FAILURE"


# ---------------------------------------------------------------------------
# Test Class: Failure Isolation
# ---------------------------------------------------------------------------

class TestFailureIsolation:
    """Tests that audit failures never interrupt business operations."""

    def test_log_create_exception_caught(self, mock_audit_service):
        """log_create must catch all exceptions and return None."""
        mock_audit_service.configs.is_audited = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
        )

        assert result is None

    def test_log_update_exception_caught(self, mock_audit_service):
        """log_update must catch all exceptions and return None."""
        mock_audit_service.configs.is_audited = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_update(
            entity_type="admin_user",
            entity_id="user-1",
        )

        assert result is None

    def test_log_delete_exception_caught(self, mock_audit_service):
        """log_delete must catch all exceptions and return None."""
        mock_audit_service.configs.is_audited = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_delete(
            entity_type="admin_user",
            entity_id="user-1",
        )

        assert result is None

    def test_log_login_exception_caught(self, mock_audit_service):
        """log_login must catch all exceptions and return None."""
        mock_audit_service.logs.log = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_login(
            user_id="admin-1",
            success=True,
        )

        assert result is None

    def test_log_logout_exception_caught(self, mock_audit_service):
        """log_logout must catch all exceptions and return None."""
        mock_audit_service.logs.log = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_logout(user_id="admin-1")

        assert result is None

    def test_log_security_event_exception_caught(self, mock_audit_service):
        """log_security_event must catch all exceptions and return None."""
        mock_audit_service.logs.log = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_security_event(
            action="access_denied",
            description="test",
        )

        assert result is None

    def test_log_system_event_exception_caught(self, mock_audit_service):
        """log_system_event must catch all exceptions and return None."""
        mock_audit_service.logs.log = MagicMock(
            side_effect=RuntimeError("DB connection lost")
        )

        result = mock_audit_service.log_system_event(
            action="startup",
            description="test",
        )

        assert result is None


# ---------------------------------------------------------------------------
# Test Class: Sensitive Data Redaction
# ---------------------------------------------------------------------------

class TestSensitiveDataRedaction:
    """Tests that sensitive fields are redacted in audit logs."""

    def test_sensitive_fields_redacted_in_new_state(self, mock_audit_service):
        """Fields listed in AuditConfig.sensitive_fields should be redacted."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"email": "test@example.com", "password": "secret123", "token": "abc"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        state = json.loads(call_kwargs["new_state"])
        assert state["email"] == "test@example.com"
        assert state["password"] == "***"
        assert state["token"] == "***"

    def test_sensitive_fields_redacted_in_previous_state(self, mock_audit_service):
        """Sensitive fields should be redacted in previous_state too."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_update(
            entity_type="admin_user",
            entity_id="user-1",
            previous_state={"password": "old_pass"},
            new_state={"password": "new_pass"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        prev = json.loads(call_kwargs["previous_state"])
        new = json.loads(call_kwargs["new_state"])
        assert prev["password"] == "***"
        assert new["password"] == "***"

    def test_non_sensitive_fields_preserved(self, mock_audit_service):
        """Non-sensitive fields should not be redacted."""
        mock_audit_service.logs.log = MagicMock(return_value=MagicMock(spec=AuditLog))

        mock_audit_service.log_create(
            entity_type="admin_user",
            entity_id="user-1",
            new_state={"email": "test@example.com", "full_name": "Test User"},
        )

        call_kwargs = mock_audit_service.logs.log.call_args[1]
        state = json.loads(call_kwargs["new_state"])
        assert state["email"] == "test@example.com"
        assert state["full_name"] == "Test User"


# ---------------------------------------------------------------------------
# Test Class: Audit Config Lookup
# ---------------------------------------------------------------------------

class TestAuditConfigLookup:
    """Tests for _should_audit() config lookup."""

    def test_should_audit_returns_true_when_enabled(self, mock_audit_service):
        """_should_audit should return True when config allows the action."""
        mock_audit_service.configs.is_audited = MagicMock(return_value=True)

        result = mock_audit_service._should_audit("admin_user", "update")

        assert result is True

    def test_should_audit_returns_false_when_disabled(self, mock_audit_service):
        """_should_audit should return False when config disallows the action."""
        mock_audit_service.configs.is_audited = MagicMock(return_value=False)

        result = mock_audit_service._should_audit("admin_user", "read")

        assert result is False


# ---------------------------------------------------------------------------
# Test Class: Context Functions
# ---------------------------------------------------------------------------

class TestContextFunctions:
    """Tests for the new context variables (endpoint, http_method)."""

    def test_set_and_get_endpoint(self):
        """set_endpoint/get_endpoint should work correctly."""
        set_endpoint("/api/test")
        assert get_endpoint() == "/api/test"
        clear_context()

    def test_set_and_get_http_method(self):
        """set_http_method/get_http_method should work correctly."""
        set_http_method("POST")
        assert get_http_method() == "POST"
        clear_context()

    def test_clear_context_resets_endpoint(self):
        """clear_context should reset endpoint to None."""
        set_endpoint("/api/test")
        clear_context()
        assert get_endpoint() is None

    def test_clear_context_resets_http_method(self):
        """clear_context should reset http_method to None."""
        set_http_method("DELETE")
        clear_context()
        assert get_http_method() is None

    def test_endpoint_default_is_none(self):
        """endpoint should default to None."""
        assert get_endpoint() is None

    def test_http_method_default_is_none(self):
        """http_method should default to None."""
        assert get_http_method() is None


# ---------------------------------------------------------------------------
# Test Class: Query API
# ---------------------------------------------------------------------------

class TestQueryAPI:
    """Tests for AuditService query methods."""

    def test_search_logs_delegates_to_repository(self, mock_audit_service):
        """search_logs should delegate to logs.search."""
        mock_audit_service.logs.search = MagicMock(return_value={"items": [], "total": 0})

        result = mock_audit_service.search_logs(page=1, limit=10, entity_type="admin_user")

        mock_audit_service.logs.search.assert_called_once_with(
            page=1, limit=10, entity_type="admin_user",
            action=None, user_id=None,
            start_date=None, end_date=None, search=None,
        )

    def test_get_entity_history_delegates_to_repository(self, mock_audit_service):
        """get_entity_history should delegate to logs.get_by_entity."""
        mock_audit_service.logs.get_by_entity = MagicMock(return_value=[])

        mock_audit_service.get_entity_history("admin_user", "user-1")

        mock_audit_service.logs.get_by_entity.assert_called_once_with("admin_user", "user-1", 100)

    def test_get_user_history_delegates_to_repository(self, mock_audit_service):
        """get_user_history should delegate to logs.get_by_user."""
        mock_audit_service.logs.get_by_user = MagicMock(return_value=[])

        mock_audit_service.get_user_history("user-1", limit=50, offset=10)

        mock_audit_service.logs.get_by_user.assert_called_once_with(
            "user-1", limit=50, offset=10, action=None
        )


# ---------------------------------------------------------------------------
# Test Class: State Diff Helper
# ---------------------------------------------------------------------------

class TestComputeDiff:
    """Tests for AuditService.compute_diff()."""

    def test_both_none_returns_empty(self):
        """Both states None should return empty dict."""
        assert AuditService.compute_diff(None, None) == {}

    def test_old_none_returns_added(self):
        """Old state None should return added keys."""
        result = AuditService.compute_diff(None, {"a": 1, "b": 2})
        assert "added" in result
        assert set(result["added"]) == {"a", "b"}

    def test_new_none_returns_removed(self):
        """New state None should return removed keys."""
        result = AuditService.compute_diff({"a": 1, "b": 2}, None)
        assert "removed" in result
        assert set(result["removed"]) == {"a", "b"}

    def test_changed_values_detected(self):
        """Changed values should be detected."""
        result = AuditService.compute_diff(
            {"a": 1, "b": 2},
            {"a": 1, "b": 3},
        )
        assert "changed" in result
        assert result["changed"]["b"]["old"] == 2
        assert result["changed"]["b"]["new"] == 3

    def test_unchanged_values_not_in_diff(self):
        """Unchanged values should not appear in diff."""
        result = AuditService.compute_diff(
            {"a": 1, "b": 2},
            {"a": 1, "b": 2},
        )
        assert result == {}
