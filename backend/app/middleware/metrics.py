"""Metrics middleware for automatic request collection.

Standalone middleware that records request count, response time, and error
metrics for every HTTP request. Integrates with MetricsService for
in-memory aggregation and periodic database flush.
"""
import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Paths to exclude from metrics (same as AuditMiddleware)
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


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that automatically records request metrics.

    Resolves the MetricsService singleton from app.state at request time.
    The singleton is created once during application lifespan startup.

    Features:
    - Records request count per endpoint
    - Records response time per endpoint
    - Records error count for 4xx/5xx responses
    - Fire-and-forget: never blocks request processing

    Usage:
        app.add_middleware(MetricsMiddleware)
    """

    def __init__(
        self,
        app: ASGIApp,
        excluded_paths: Optional[set] = None,
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or DEFAULT_EXCLUDED_PATHS

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        # Resolve singleton from app.state at request time
        metrics_service = getattr(request.app.state, "metrics_service", None)
        if metrics_service is None:
            return await call_next(request)

        start_time = time.time()
        endpoint = request.url.path
        method = request.method

        response_status = 500
        try:
            response = await call_next(request)
            response_status = response.status_code
            return response
        except Exception:
            response_status = 500
            raise
        finally:
            response_time_ms = (time.time() - start_time) * 1000
            try:
                metrics_service.record_request(
                    endpoint=endpoint,
                    method=method,
                    status_code=response_status,
                    response_time_ms=response_time_ms,
                )
            except Exception as e:
                # Fire-and-forget: never block request processing
                logger.debug("Metrics recording failed: %s", e)
