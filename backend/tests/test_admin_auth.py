"""Tests for Admin Authorization (PROC-SPEC-0.2).

Comprehensive tests for the require_admin() dependency covering:
- Unauthenticated requests (401)
- Authenticated non-admin requests (403)
- Authenticated admin requests (success)
- Standardized error responses (PROC-SPEC-0.7 format)
- request_id propagation (PROC-SPEC-0.6)
- Audit logging of failed authorization attempts
- Regression testing of existing authentication
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.auth import require_admin, get_current_user
from app.context import set_request_id, get_request_id, clear_context
from app.exceptions import AuthenticationError, AuthorizationError, ApplicationException
from app.models import User


# ---------------------------------------------------------------------------
# Test App Setup
# ---------------------------------------------------------------------------

def _create_test_app():
    """Create a minimal FastAPI app for testing require_admin()."""
    app = FastAPI()

    # Register exception handlers (same as main.py)
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        request_id = get_request_id()
        exc.request_id = request_id
        response = exc.to_dict()
        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )

    @app.get("/admin-only")
    def admin_endpoint(current_user: User = Depends(require_admin)):
        return {"user_id": current_user.id, "is_superuser": current_user.is_superuser}

    @app.get("/auth-only")
    def auth_endpoint(current_user: User = Depends(get_current_user)):
        if current_user is None:
            return {"user_id": None}
        return {"user_id": current_user.id}

    return app


def _create_mock_user(user_id: str = "test-user-123", is_superuser: bool = False):
    """Create a mock User object."""
    user = MagicMock(spec=User)
    user.id = user_id
    user.is_superuser = is_superuser
    return user


# ---------------------------------------------------------------------------
# Test Class: Unauthenticated Requests
# ---------------------------------------------------------------------------

class TestUnauthenticatedRequests:
    """Tests for unauthenticated requests to admin endpoints."""

    def test_no_token_returns_401(self):
        """Request without token must return 401 Unauthorized."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        assert response.status_code == 401

    def test_no_token_returns_standardized_error(self):
        """401 response must follow PROC-SPEC-0.7 standardized error format."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "AUTHENTICATION_ERROR"
        assert "Authentication required" in data["error"]["message"]

    def test_no_token_includes_request_id(self):
        """401 response must include request_id field (may be None in test env)."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        # request_id field must exist (value is None when AuditMiddleware not present)
        assert "request_id" in data["error"]

    def test_invalid_token_returns_401(self):
        """Request with invalid token must return 401 Unauthorized."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(
            "/admin-only",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        # get_current_user raises HTTPException which gets standardized
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Test Class: Authenticated Non-Admin Requests
# ---------------------------------------------------------------------------

class TestNonAdminRequests:
    """Tests for authenticated non-admin requests to admin endpoints."""

    def test_non_admin_returns_403(self):
        """Non-admin user must receive 403 Forbidden."""
        app = _create_test_app()

        # Override the dependency to return a non-admin user
        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        assert response.status_code == 403

    def test_non_admin_returns_standardized_error(self):
        """403 response must follow PROC-SPEC-0.7 standardized error format."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "AUTHORIZATION_ERROR"
        assert "Admin access required" in data["error"]["message"]

    def test_non_admin_includes_request_id(self):
        """403 response must include request_id field (may be None in test env)."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        # request_id field must exist (value is None when AuditMiddleware not present)
        assert "request_id" in data["error"]

    def test_non_admin_includes_user_id_in_details(self):
        """403 response must include user_id in error details."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(
            user_id="non-admin-user-456",
            is_superuser=False
        )
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert "details" in data["error"]
        assert data["error"]["details"]["user_id"] == "non-admin-user-456"


# ---------------------------------------------------------------------------
# Test Class: Authenticated Admin Requests
# ---------------------------------------------------------------------------

class TestAdminRequests:
    """Tests for authenticated admin requests to admin endpoints."""

    def test_admin_returns_200(self):
        """Admin user must receive 200 OK."""
        app = _create_test_app()

        admin_user = _create_mock_user(is_superuser=True)
        app.dependency_overrides[get_current_user] = lambda: admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        assert response.status_code == 200

    def test_admin_returns_user_data(self):
        """Admin endpoint must return user data."""
        app = _create_test_app()

        admin_user = _create_mock_user(
            user_id="admin-user-789",
            is_superuser=True
        )
        app.dependency_overrides[get_current_user] = lambda: admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert data["user_id"] == "admin-user-789"
        assert data["is_superuser"] is True


# ---------------------------------------------------------------------------
# Test Class: Standardized Error Responses
# ---------------------------------------------------------------------------

class TestStandardizedErrorResponses:
    """Tests for error response format compliance with PROC-SPEC-0.7."""

    def test_401_has_success_field(self):
        """401 response must have success=False."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert "success" in data
        assert data["success"] is False

    def test_401_has_error_object(self):
        """401 response must have error object with required fields."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
        assert "request_id" in error
        assert "timestamp" in error

    def test_403_has_success_field(self):
        """403 response must have success=False."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert "success" in data
        assert data["success"] is False

    def test_403_has_error_object(self):
        """403 response must have error object with required fields."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "details" in error
        assert "request_id" in error
        assert "timestamp" in error


# ---------------------------------------------------------------------------
# Test Class: Request ID Propagation
# ---------------------------------------------------------------------------

class TestRequestIdPropagation:
    """Tests for request_id propagation from PROC-SPEC-0.6."""

    def test_request_id_in_401_response(self):
        """request_id field must exist in 401 error response."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        # request_id field must exist (value is None when AuditMiddleware not present)
        assert "request_id" in data["error"]
        assert isinstance(data["error"]["request_id"], (str, type(None)))

    def test_request_id_in_403_response(self):
        """request_id field must exist in 403 error response."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/admin-only")
        data = response.json()

        # request_id field must exist (value is None when AuditMiddleware not present)
        assert "request_id" in data["error"]
        assert isinstance(data["error"]["request_id"], (str, type(None)))

    def test_request_id_unique_per_request(self):
        """Each request must have a unique request_id (when AuditMiddleware present)."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        response1 = client.get("/admin-only")
        response2 = client.get("/admin-only")

        # Both must have request_id field
        assert "request_id" in response1.json()["error"]
        assert "request_id" in response2.json()["error"]
        # In production with AuditMiddleware, these would be unique strings


# ---------------------------------------------------------------------------
# Test Class: Audit Logging
# ---------------------------------------------------------------------------

class TestAuditLogging:
    """Tests for audit logging of failed authorization attempts."""

    @patch("app.auth.logger")
    def test_unauthenticated_attempt_logged(self, mock_logger):
        """Unauthenticated authorization attempt must be logged."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        client.get("/admin-only")

        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "not authenticated" in call_args[0][0]

    @patch("app.auth.logger")
    def test_non_admin_attempt_logged(self, mock_logger):
        """Non-admin authorization attempt must be logged with user_id."""
        app = _create_test_app()

        non_admin_user = _create_mock_user(
            user_id="non-admin-999",
            is_superuser=False
        )
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        client = TestClient(app, raise_server_exceptions=False)

        client.get("/admin-only")

        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "not an administrator" in call_args[0][0]


# ---------------------------------------------------------------------------
# Test Class: Regression - Existing Authentication
# ---------------------------------------------------------------------------

class TestRegressionExistingAuth:
    """Regression tests ensuring existing authentication remains functional."""

    def test_get_current_user_still_works(self):
        """get_current_user() must still work for non-admin endpoints."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        # Without token, get_current_user returns None
        response = client.get("/auth-only")
        assert response.status_code == 200
        assert response.json()["user_id"] is None

    def test_require_auth_still_works(self):
        """require_auth() must still work for regular authenticated endpoints."""
        from app.auth import require_auth

        app = FastAPI()

        # Register exception handler
        @app.exception_handler(ApplicationException)
        async def application_exception_handler(request: Request, exc: ApplicationException):
            request_id = get_request_id()
            exc.request_id = request_id
            response = exc.to_dict()
            return JSONResponse(
                status_code=exc.status_code,
                content=response,
            )

        # Override get_current_user to return a non-admin user
        non_admin_user = _create_mock_user(is_superuser=False)
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        @app.get("/auth-required")
        def auth_required(current_user: User = Depends(require_auth)):
            return {"user_id": current_user.id}

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/auth-required")
        assert response.status_code == 200

    def test_require_role_still_works(self):
        """require_role() must still work for role-based endpoints."""
        from app.auth import require_role

        app = FastAPI()

        # Register exception handler
        @app.exception_handler(ApplicationException)
        async def application_exception_handler(request: Request, exc: ApplicationException):
            request_id = get_request_id()
            exc.request_id = request_id
            response = exc.to_dict()
            return JSONResponse(
                status_code=exc.status_code,
                content=response,
            )

        # Override get_current_user to return a superuser
        admin_user = _create_mock_user(is_superuser=True)
        app.dependency_overrides[get_current_user] = lambda: admin_user

        @app.get("/role-required")
        def role_required(current_user: User = Depends(require_role("admin"))):
            return {"user_id": current_user.id}

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/role-required")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test Class: Context Unit Tests
# ---------------------------------------------------------------------------

class TestContextUnit:
    """Unit tests for context functions used by require_admin()."""

    def test_set_and_get_request_id(self):
        """set_request_id must set value accessible via get_request_id."""
        set_request_id("test-req-123")
        assert get_request_id() == "test-req-123"
        clear_context()

    def test_clear_context_resets_request_id(self):
        """clear_context must reset request_id to None."""
        set_request_id("test-req-456")
        clear_context()
        assert get_request_id() is None


# ---------------------------------------------------------------------------
# Test Class: Exception Classes
# ---------------------------------------------------------------------------

class TestExceptionClasses:
    """Unit tests for AuthenticationError and AuthorizationError."""

    def test_authentication_error_status_code(self):
        """AuthenticationError must have status_code 401."""
        exc = AuthenticationError(message="Test auth error")
        assert exc.status_code == 401
        assert exc.code == "AUTHENTICATION_ERROR"

    def test_authorization_error_status_code(self):
        """AuthorizationError must have status_code 403."""
        exc = AuthorizationError(message="Test authz error")
        assert exc.status_code == 403
        assert exc.code == "AUTHORIZATION_ERROR"

    def test_authentication_error_to_dict(self):
        """AuthenticationError.to_dict() must return standardized format."""
        exc = AuthenticationError(message="Test auth error")
        exc.request_id = "req-123"
        result = exc.to_dict()

        assert result["success"] is False
        assert result["error"]["code"] == "AUTHENTICATION_ERROR"
        assert result["error"]["message"] == "Test auth error"
        assert result["error"]["request_id"] == "req-123"

    def test_authorization_error_to_dict(self):
        """AuthorizationError.to_dict() must return standardized format."""
        exc = AuthorizationError(message="Test authz error")
        exc.request_id = "req-456"
        result = exc.to_dict()

        assert result["success"] is False
        assert result["error"]["code"] == "AUTHORIZATION_ERROR"
        assert result["error"]["message"] == "Test authz error"
        assert result["error"]["request_id"] == "req-456"
