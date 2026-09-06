"""Error middleware for automatic exception capture.

Automatically captures unhandled exceptions and logs them to the error log.
Integrates with the ErrorService for persistent storage and the AuditMiddleware
for correlation.
"""
import logging
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..context import get_request_id, get_user_id
from ..exceptions import ApplicationException
from ..notifications import notify_critical_error

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically captures unhandled exceptions.

    Features:
    - Captures all unhandled exceptions
    - Logs to ErrorService with full context
    - Returns structured error response
    - Integrates with AuditMiddleware via correlation IDs
    - Never breaks the application

    Usage:
        from app.middleware.error import ErrorMiddleware
        app.add_middleware(ErrorMiddleware)
    """

    def __init__(
        self,
        app: ASGIApp,
        debug: bool = False,
        exclude_paths: Optional[set] = None,
    ):
        super().__init__(app)
        self.debug = debug
        self.exclude_paths = exclude_paths or {"/", "/health", "/healthz", "/ping"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        start_time = time.time()

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Get request context
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            endpoint = request.url.path
            http_method = request.method
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            correlation_id = getattr(request.state, "correlation_id", request_id)
            user_id = getattr(request.state, "user_id", None)
            session_id = getattr(request.state, "session_id", None)

            # Extract router name from endpoint (e.g. /api/errors/stats -> errors)
            router_name = self._extract_router(endpoint)

            # Log the error
            error_id = "logging-failed"
            try:
                from ..database import SessionLocal
                from ..services.error_service import ErrorService

                db = SessionLocal()
                try:
                    service = ErrorService(db)
                    error_log = service.log_exception(
                        e,
                        endpoint=endpoint,
                        http_method=http_method,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        processing_time_ms=processing_time_ms,
                        user_id=user_id,
                        session_id=session_id,
                        request_id=request_id,
                        correlation_id=correlation_id,
                        router=router_name,
                    )
                    error_id = error_log.id
                finally:
                    db.close()
            except Exception as log_exc:
                logger.warning("Failed to log error to ErrorService: %s", log_exc)

            # Trigger notification for critical errors
            if not isinstance(e, ApplicationException) or e.status_code >= 500:
                try:
                    notify_critical_error(
                        error_code=getattr(e, "code", "INTERNAL_ERROR"),
                        message=str(e),
                        endpoint=endpoint,
                        http_method=http_method,
                        request_id=request_id,
                        user_id=user_id,
                        status_code=500,
                    )
                except Exception as notify_exc:
                    logger.warning("Failed to trigger critical error alert: %s", notify_exc)

            # Return standardized error response
            status_code = 500
            if isinstance(e, ApplicationException):
                status_code = e.status_code

            response_content = {
                "success": False,
                "error": {
                    "code": getattr(e, "code", "INTERNAL_ERROR"),
                    "message": "An unexpected error occurred" if not self.debug else str(e),
                    "details": getattr(e, "details", {}),
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }

            return JSONResponse(
                status_code=status_code,
                content=response_content,
                headers={
                    "X-Error-ID": getattr(e, "code", "INTERNAL_ERROR"),
                    "X-Request-ID": request_id,
                    "X-Correlation-ID": correlation_id,
                },
            )

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _extract_router(endpoint: str) -> Optional[str]:
        """Extract router name from endpoint path.

        Examples:
            /api/errors/stats -> errors
            /api/templates -> templates
            /api/health -> health
            /storage/templates/foo.jpg -> storage
        """
        parts = [p for p in endpoint.split("/") if p]
        if len(parts) >= 2 and parts[0] == "api":
            return parts[1]
        if parts:
            return parts[0]
        return None


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware that handles specific HTTP error responses.

    Logs 4xx/5xx responses to the error log for monitoring.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)

        # Log error responses (4xx/5xx)
        if response.status_code >= 400:
            processing_time_ms = int((time.time() - start_time) * 1000)
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            endpoint = request.url.path
            http_method = request.method
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            correlation_id = getattr(request.state, "correlation_id", request_id)
            user_id = getattr(request.state, "user_id", None)
            session_id = getattr(request.state, "session_id", None)
            router_name = self._extract_router(endpoint)

            try:
                from ..database import SessionLocal
                from ..services.error_service import ErrorService

                db = SessionLocal()
                try:
                    service = ErrorService(db)
                    service.log_api_error(
                        status_code=response.status_code,
                        detail=f"HTTP {response.status_code}",
                        endpoint=endpoint,
                        http_method=http_method,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        processing_time_ms=processing_time_ms,
                        user_id=user_id,
                        session_id=session_id,
                        request_id=request_id,
                        correlation_id=correlation_id,
                        router=router_name,
                    )
                finally:
                    db.close()
            except Exception as e:
                logger.warning("Failed to log API error to ErrorService: %s", e)

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _extract_router(endpoint: str) -> Optional[str]:
        """Extract router name from endpoint path.

        Examples:
            /api/errors/stats -> errors
            /api/templates -> templates
            /api/health -> health
            /storage/templates/foo.jpg -> storage
        """
        parts = [p for p in endpoint.split("/") if p]
        if len(parts) >= 2 and parts[0] == "api":
            return parts[1]
        if parts:
            return parts[0]
        return None


def create_error_middleware(
    debug: bool = False,
    exclude_paths: Optional[set] = None,
) -> ErrorMiddleware:
    """Factory function to create ErrorMiddleware with custom settings."""
    return ErrorMiddleware(
        app=None,  # Will be set by FastAPI
        debug=debug,
        exclude_paths=exclude_paths,
    )
