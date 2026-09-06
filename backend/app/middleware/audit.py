"""Audit middleware for automatic request logging.

Automatically logs all HTTP requests with timing, user context, and
error information. Integrates with the AuditService for persistent storage.
"""
import json
import logging
import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..context import set_request_id, set_user_id, set_session_id, set_endpoint, set_http_method, clear_context

logger = logging.getLogger(__name__)


# Paths to exclude from audit logging (health checks, docs, etc.)
DEFAULT_EXCLUDED_PATHS = {
    "/",
    "/health",
    "/healthz",
    "/ping",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
}


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically logs HTTP requests to the audit log.

    Features:
    - Generates unique request_id and correlation_id
    - Captures user context from request state
    - Measures processing time
    - Logs errors and exceptions
    - Excludes health check and docs endpoints

    Usage:
        from app.middleware.audit import AuditMiddleware
        app.add_middleware(AuditMiddleware)
    """

    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: Optional[set] = None,
        log_request_body: bool = False,
        max_body_size: int = 1024,
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS
        self.log_request_body = log_request_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Generate request IDs
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID", request_id)

        # Store in request state for downstream use
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        # Set request_id in context (available immediately)
        set_request_id(request_id)

        # Capture request context
        start_time = time.time()
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        endpoint = request.url.path
        http_method = request.method

        # Set endpoint and http_method in context (now defined)
        set_endpoint(endpoint)
        set_http_method(http_method)

        # Get user context if available
        user_id = getattr(request.state, "user_id", None)
        session_id = getattr(request.state, "session_id", None)

        # Optionally capture request body
        request_body = None
        if self.log_request_body and http_method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if len(body_bytes) <= self.max_body_size:
                    request_body = body_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                logger.debug("Failed to capture request body: %s", e)

        # Process request
        error_message = None
        response_status = 500
        try:
            response = await call_next(request)
            response_status = response.status_code

            # Add X-Request-ID header to ALL responses
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Log to audit service (fire-and-forget to avoid blocking)
            try:
                from ..database import SessionLocal
                from ..services.audit_service import AuditService

                db = SessionLocal()
                try:
                    service = AuditService(db)
                    service._log_request(
                        user_id=user_id,
                        session_id=session_id,
                        request_id=request_id,
                        correlation_id=correlation_id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        endpoint=endpoint,
                        http_method=http_method,
                        response_status=response_status,
                        processing_time_ms=processing_time_ms,
                        request_body=request_body,
                        error_message=error_message,
                    )
                finally:
                    db.close()
            except Exception as e:
                # Never let audit logging break the request
                logger.warning("Audit logging failed: %s", e)

            # Clear context at end of request
            clear_context()

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check for forwarded headers
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"


class AuditContextMiddleware(BaseHTTPMiddleware):
    """Middleware that extracts and stores user context from JWT tokens.

    This middleware should be placed BEFORE the AuditMiddleware to ensure
    user context is available for logging.

    Usage:
        app.add_middleware(AuditContextMiddleware)
        app.add_middleware(AuditMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Try to extract user context from Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from ..auth import verify_token
                token = auth_header.split(" ")[1]
                payload = verify_token(token)
                if payload:
                    user_id = payload.get("sub")
                    session_id = payload.get("session_id")
                    request.state.user_id = user_id
                    request.state.session_id = session_id

                    # Set in contextvars for service-layer access
                    if user_id:
                        set_user_id(user_id)
                    if session_id:
                        set_session_id(session_id)
            except Exception as e:
                logger.debug("Failed to extract user context from token: %s", e)

        return await call_next(request)


def create_audit_middleware(
    excluded_paths: Optional[set] = None,
    log_request_body: bool = False,
    max_body_size: int = 1024,
) -> AuditMiddleware:
    """Factory function to create AuditMiddleware with custom settings."""
    return AuditMiddleware(
        app=None,  # Will be set by FastAPI
        excluded_paths=excluded_paths,
        log_request_body=log_request_body,
        max_body_size=max_body_size,
    )
