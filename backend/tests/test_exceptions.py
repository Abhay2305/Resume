"""Tests for PROC-SPEC-0.7: Global Exception Handling.

Tests exception hierarchy, error response format, and request_id propagation.
"""
import pytest
from datetime import datetime, timezone
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import (
    ApplicationException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    BusinessRuleError,
    RateLimitError,
    ExternalServiceError,
    DatabaseError,
    InternalServerError,
    BadRequestError,
    ServiceUnavailableError,
    TimeoutError,
    FileStorageError,
    ErrorDetail,
)
from app.context import get_request_id, clear_context, set_request_id


# ---------------------------------------------------------------------------
# Test App Setup
# ---------------------------------------------------------------------------

def _create_test_app():
    """Create a minimal test app with exception handlers and middleware registered."""
    test_app = FastAPI()

    # Register AuditMiddleware to set request_id in context (from PROC-SPEC-0.6)
    from app.middleware.audit import AuditMiddleware
    test_app.add_middleware(AuditMiddleware)

    # Register exception handlers (same as main.py)
    @test_app.exception_handler(ApplicationException)
    async def application_exception_handler(request: Request, exc: ApplicationException):
        request_id = get_request_id()
        exc.request_id = request_id
        response = exc.to_dict()
        return JSONResponse(status_code=exc.status_code, content=response)

    @test_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = get_request_id()
        errors = []
        for error in exc.errors():
            loc = error.get("loc", [])
            field = " -> ".join(str(part) for part in loc)
            msg = error.get("msg", "Invalid value")
            errors.append({"field": field, "message": msg})
        response = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {},
                "errors": errors,
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return JSONResponse(status_code=422, content=response)

    @test_app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = get_request_id()
        response = {
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "details": {},
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return JSONResponse(status_code=exc.status_code, content=response)

    @test_app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = get_request_id()
        response = {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {},
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return JSONResponse(status_code=500, content=response)

    class ItemCreate(BaseModel):
        name: str = Field(min_length=1)
        value: int = Field(ge=0)

    @test_app.get("/api/test-ok")
    async def test_ok():
        return {"status": "ok"}

    @test_app.get("/api/test-not-found")
    async def test_not_found():
        raise NotFoundError(message="Item not found", details={"item_id": "abc-123"})

    @test_app.get("/api/test-validation")
    async def test_validation():
        raise ValidationError(
            message="Invalid input",
            errors=[ErrorDetail(field="email", message="Invalid email format")],
        )

    @test_app.get("/api/test-auth")
    async def test_auth():
        raise AuthenticationError(message="Token expired")

    @test_app.get("/api/test-forbidden")
    async def test_forbidden():
        raise AuthorizationError(message="Insufficient permissions")

    @test_app.get("/api/test-conflict")
    async def test_conflict():
        raise ConflictError(message="Resource already exists")

    @test_app.get("/api/test-business-rule")
    async def test_business_rule():
        raise BusinessRuleError(message="Cannot delete active subscription")

    @test_app.get("/api/test-rate-limit")
    async def test_rate_limit():
        raise RateLimitError(message="Too many requests")

    @test_app.get("/api/test-external")
    async def test_external():
        raise ExternalServiceError(message="AI provider unavailable")

    @test_app.get("/api/test-database")
    async def test_database():
        raise DatabaseError(message="Connection pool exhausted")

    @test_app.get("/api/test-internal")
    async def test_internal():
        raise InternalServerError(message="Something went wrong")

    @test_app.get("/api/test-unhandled")
    async def test_unhandled():
        raise RuntimeError("Unexpected runtime error")

    @test_app.get("/api/test-http-exception")
    async def test_http_exception():
        raise HTTPException(status_code=404, detail="Resource not found")

    @test_app.post("/api/test-pydantic-validation")
    async def test_pydantic_validation(item: ItemCreate):
        return {"item": item.dict()}

    @test_app.get("/api/test-context")
    async def test_context():
        return {"request_id": get_request_id()}

    return test_app


# ---------------------------------------------------------------------------
# Test Classes
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    """Tests for the exception class hierarchy."""

    def test_application_exception_is_base(self):
        assert issubclass(ValidationError, ApplicationException)
        assert issubclass(AuthenticationError, ApplicationException)
        assert issubclass(AuthorizationError, ApplicationException)
        assert issubclass(NotFoundError, ApplicationException)
        assert issubclass(ConflictError, ApplicationException)
        assert issubclass(BusinessRuleError, ApplicationException)
        assert issubclass(RateLimitError, ApplicationException)
        assert issubclass(ExternalServiceError, ApplicationException)
        assert issubclass(DatabaseError, ApplicationException)
        assert issubclass(InternalServerError, ApplicationException)

    def test_application_exception_status_codes(self):
        assert ValidationError.status_code == 422
        assert AuthenticationError.status_code == 401
        assert AuthorizationError.status_code == 403
        assert NotFoundError.status_code == 404
        assert ConflictError.status_code == 409
        assert BusinessRuleError.status_code == 400
        assert RateLimitError.status_code == 429
        assert ExternalServiceError.status_code == 502
        assert DatabaseError.status_code == 500
        assert InternalServerError.status_code == 500

    def test_application_exception_default_codes(self):
        assert ValidationError.default_code == "VALIDATION_ERROR"
        assert AuthenticationError.default_code == "AUTHENTICATION_ERROR"
        assert AuthorizationError.default_code == "AUTHORIZATION_ERROR"
        assert NotFoundError.default_code == "NOT_FOUND"
        assert ConflictError.default_code == "CONFLICT"
        assert BusinessRuleError.default_code == "BUSINESS_RULE_ERROR"
        assert RateLimitError.default_code == "RATE_LIMIT_EXCEEDED"
        assert ExternalServiceError.default_code == "EXTERNAL_SERVICE_ERROR"
        assert DatabaseError.default_code == "DATABASE_ERROR"
        assert InternalServerError.default_code == "INTERNAL_ERROR"

    def test_application_exception_to_dict(self):
        exc = NotFoundError(message="Not found", details={"id": "123"})
        exc.request_id = "req-abc"
        d = exc.to_dict()
        assert d["success"] is False
        assert d["error"]["code"] == "NOT_FOUND"
        assert d["error"]["message"] == "Not found"
        assert d["error"]["details"] == {"id": "123"}
        assert d["error"]["request_id"] == "req-abc"
        assert "timestamp" in d["error"]

    def test_application_exception_with_errors(self):
        exc = ValidationError(
            message="Validation failed",
            errors=[ErrorDetail(field="email", message="required")],
        )
        d = exc.to_dict()
        assert "errors" in d["error"]
        assert len(d["error"]["errors"]) == 1
        assert d["error"]["errors"][0]["field"] == "email"
        assert d["error"]["errors"][0]["message"] == "required"

    def test_error_detail_to_dict(self):
        detail = ErrorDetail(field="name", message="required")
        assert detail.to_dict() == {"field": "name", "message": "required"}


class TestStandardErrorResponse:
    """Tests for standardized error response format."""

    def test_not_found_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["error"]["message"] == "Item not found"
        assert data["error"]["details"]["item_id"] == "abc-123"
        assert "request_id" in data["error"]
        assert "timestamp" in data["error"]

    def test_validation_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-validation")
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "errors" in data["error"]

    def test_auth_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-auth")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AUTHENTICATION_ERROR"

    def test_forbidden_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-forbidden")
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "AUTHORIZATION_ERROR"

    def test_conflict_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-conflict")
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "CONFLICT"

    def test_business_rule_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-business-rule")
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "BUSINESS_RULE_ERROR"

    def test_rate_limit_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-rate-limit")
        assert response.status_code == 429
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_external_service_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-external")
        assert response.status_code == 502
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "EXTERNAL_SERVICE_ERROR"

    def test_database_error_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-database")
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "DATABASE_ERROR"

    def test_internal_error_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-internal")
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INTERNAL_ERROR"


class TestRequestIdPropagation:
    """Tests for request_id propagation in error responses."""

    def test_request_id_in_error_response(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-not-found")
        data = response.json()
        assert "request_id" in data["error"]
        assert data["error"]["request_id"] is not None

    def test_request_id_matches_header(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-not-found")
        header_id = response.headers.get("X-Request-ID")
        body_id = response.json()["error"]["request_id"]
        assert header_id == body_id

    def test_request_id_unique_per_request(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        r1 = client.get("/api/test-not-found")
        r2 = client.get("/api/test-not-found")
        assert r1.json()["error"]["request_id"] != r2.json()["error"]["request_id"]

    def test_request_id_on_all_error_types(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        endpoints = [
            "/api/test-not-found",
            "/api/test-validation",
            "/api/test-auth",
            "/api/test-forbidden",
            "/api/test-internal",
        ]
        for ep in endpoints:
            response = client.get(ep)
            data = response.json()
            assert "request_id" in data["error"], f"Missing request_id on {ep}"
            assert data["error"]["request_id"] is not None, f"Null request_id on {ep}"


class TestSecurity:
    """Tests for security - no sensitive information leakage."""

    def test_no_stack_trace_in_production(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-unhandled")
        data = response.json()
        error_str = str(data)
        assert "traceback" not in error_str.lower()
        assert "File \"" not in error_str
        assert "line " not in error_str

    def test_no_internal_path_leakage(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-unhandled")
        data = response.json()
        error_str = str(data)
        assert "backend/app" not in error_str
        assert "site-packages" not in error_str

    def test_unhandled_exception_returns_generic_message(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-unhandled")
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"


class TestPydanticValidationErrors:
    """Tests for FastAPI/Pydantic validation error standardization."""

    def test_pydantic_validation_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/test-pydantic-validation", json={})
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Validation failed"
        assert "errors" in data["error"]
        assert len(data["error"]["errors"]) > 0

    def test_pydantic_validation_includes_field_info(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/test-pydantic-validation", json={})
        data = response.json()
        errors = data["error"]["errors"]
        assert any("name" in e["field"] for e in errors)

    def test_pydantic_validation_has_request_id(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/test-pydantic-validation", json={})
        data = response.json()
        assert "request_id" in data["error"]


class TestHTTPException:
    """Tests for FastAPI HTTPException standardization."""

    def test_http_exception_returns_standard_format(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-http-exception")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "HTTP_404"
        assert data["error"]["message"] == "Resource not found"
        assert "request_id" in data["error"]


class TestSuccessfulResponse:
    """Tests for successful responses (no error format)."""

    def test_successful_response_not_affected(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-ok")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "error" not in data

    def test_successful_response_has_request_id_header(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/test-ok")
        assert "X-Request-ID" in response.headers


class TestNewExceptionClasses:
    """Tests for newly added exception classes per SPEC-0.7."""

    def test_bad_request_error_status_code(self):
        assert BadRequestError.status_code == 400
        assert BadRequestError.default_code == "BAD_REQUEST"

    def test_service_unavailable_error_status_code(self):
        assert ServiceUnavailableError.status_code == 503
        assert ServiceUnavailableError.default_code == "SERVICE_UNAVAILABLE"

    def test_timeout_error_status_code(self):
        assert TimeoutError.status_code == 504
        assert TimeoutError.default_code == "TIMEOUT"

    def test_file_storage_error_status_code(self):
        assert FileStorageError.status_code == 500
        assert FileStorageError.default_code == "FILE_STORAGE_ERROR"

    def test_all_new_exceptions_are_application_exception(self):
        assert issubclass(BadRequestError, ApplicationException)
        assert issubclass(ServiceUnavailableError, ApplicationException)
        assert issubclass(TimeoutError, ApplicationException)
        assert issubclass(FileStorageError, ApplicationException)

    def test_bad_request_error_to_dict(self):
        exc = BadRequestError(message="Invalid JSON", details={"line": 1})
        d = exc.to_dict()
        assert d["success"] is False
        assert d["error"]["code"] == "BAD_REQUEST"
        assert d["error"]["message"] == "Invalid JSON"
        assert d["error"]["details"]["line"] == 1

    def test_service_unavailable_error_to_dict(self):
        exc = ServiceUnavailableError(message="AI provider down")
        d = exc.to_dict()
        assert d["error"]["code"] == "SERVICE_UNAVAILABLE"

    def test_timeout_error_to_dict(self):
        exc = TimeoutError(message="Operation timed out")
        d = exc.to_dict()
        assert d["error"]["code"] == "TIMEOUT"

    def test_file_storage_error_to_dict(self):
        exc = FileStorageError(message="Upload failed")
        d = exc.to_dict()
        assert d["error"]["code"] == "FILE_STORAGE_ERROR"


class TestCriticalErrorNotification:
    """Tests for critical error notification trigger (AC-6)."""

    def test_notify_critical_error_is_called_on_500(self):
        """Verify notify_critical_error is invoked for unhandled 500 exceptions."""
        from unittest.mock import patch
        from app.middleware.error import ErrorMiddleware

        # Create test app WITH ErrorMiddleware (where notification trigger lives)
        test_app = FastAPI()
        from app.middleware.audit import AuditMiddleware
        test_app.add_middleware(AuditMiddleware)
        test_app.add_middleware(ErrorMiddleware)

        @test_app.get("/api/test-unhandled")
        async def test_unhandled():
            raise RuntimeError("Unexpected runtime error")

        client = TestClient(test_app, raise_server_exceptions=False)

        with patch("app.middleware.error.notify_critical_error") as mock_notify:
            response = client.get("/api/test-unhandled")
            assert response.status_code == 500
            mock_notify.assert_called_once()
            call_kwargs = mock_notify.call_args[1]
            assert call_kwargs["status_code"] == 500
            assert "error_code" in call_kwargs
            assert "endpoint" in call_kwargs
            assert "request_id" in call_kwargs

    def test_notify_not_called_on_4xx(self):
        """Verify notify_critical_error is NOT called for 4xx client errors."""
        from unittest.mock import patch
        from app.middleware.error import ErrorMiddleware

        test_app = FastAPI()
        from app.middleware.audit import AuditMiddleware
        test_app.add_middleware(AuditMiddleware)
        test_app.add_middleware(ErrorMiddleware)

        @test_app.get("/api/test-not-found")
        async def test_not_found():
            from app.exceptions import NotFoundError
            raise NotFoundError(message="Not found")

        client = TestClient(test_app, raise_server_exceptions=False)

        with patch("app.middleware.error.notify_critical_error") as mock_notify:
            response = client.get("/api/test-not-found")
            assert response.status_code == 404
            mock_notify.assert_not_called()

    def test_error_info_has_request_id_field(self):
        """Verify ErrorInfo model includes request_id field."""
        from app.utils import ErrorInfo
        info = ErrorInfo(code="TEST", message="test", request_id="req-123")
        assert info.request_id == "req-123"

    def test_error_info_request_id_optional(self):
        """Verify ErrorInfo request_id defaults to None."""
        from app.utils import ErrorInfo
        info = ErrorInfo(code="TEST", message="test")
        assert info.request_id is None
