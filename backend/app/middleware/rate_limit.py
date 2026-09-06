"""Rate Limiting Middleware.

Provides in-memory rate limiting for API endpoints.
Uses sliding window counter algorithm for accurate rate limiting.
"""
import logging
import time
from collections import defaultdict
from typing import Callable, Optional, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """In-memory rate limiter using sliding window counter.
    
    Usage:
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # In middleware:
        is_allowed, retry_after = limiter.check(client_ip)
        if not is_allowed:
            return Response(status_code=429, headers={"Retry-After": str(retry_after)})
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        
    def _cleanup(self, key: str, current_time: float):
        """Remove expired requests from the window."""
        cutoff_time = current_time - self.window_seconds
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff_time
        ]
    
    def check(self, key: str) -> Tuple[bool, Optional[int]]:
        """Check if a request is allowed.
        
        Args:
            key: Rate limit key (e.g., IP address, user ID)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            retry_after_seconds is None if allowed
        """
        current_time = time.time()
        self._cleanup(key, current_time)
        
        request_count = len(self._requests[key])
        
        if request_count >= self.max_requests:
            # Calculate retry-after based on oldest request in window
            oldest_request = self._requests[key][0]
            retry_after = int(self.window_seconds - (current_time - oldest_request)) + 1
            return False, retry_after
        
        self._requests[key].append(current_time)
        return True, None
    
    def reset(self, key: str):
        """Reset rate limit for a key."""
        self._requests.pop(key, None)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API endpoints.
    
    Supports per-endpoint configuration with different limits.
    """
    
    def __init__(
        self,
        app,
        default_max_requests: int = 100,
        default_window_seconds: int = 60,
        auth_max_requests: int = 10,
        auth_window_seconds: int = 60,
        login_max_requests: int = 5,
        login_window_seconds: int = 60,
        register_max_requests: int = 3,
        register_window_seconds: int = 60,
    ):
        """Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            default_max_requests: Default max requests per window
            default_window_seconds: Default window size in seconds
            auth_max_requests: Max requests for auth endpoints per window
            auth_window_seconds: Window size for auth endpoints in seconds
            login_max_requests: Max requests for login endpoint per window
            login_window_seconds: Window size for login endpoint in seconds
            register_max_requests: Max requests for register endpoint per window
            register_window_seconds: Window size for register endpoint in seconds
        """
        super().__init__(app)
        self.default_limiter = RateLimiter(
            max_requests=default_max_requests,
            window_seconds=default_window_seconds,
        )
        self.auth_limiter = RateLimiter(
            max_requests=auth_max_requests,
            window_seconds=auth_window_seconds,
        )
        self.login_limiter = RateLimiter(
            max_requests=login_max_requests,
            window_seconds=login_window_seconds,
        )
        self.register_limiter = RateLimiter(
            max_requests=register_max_requests,
            window_seconds=register_window_seconds,
        )
        self._path_limiters: dict[str, RateLimiter] = {}
        
    def _get_limiter_for_path(self, path: str) -> Optional[RateLimiter]:
        """Get the appropriate rate limiter for a path."""
        # Login endpoint: stricter limit (5 req/min per spec)
        if path.startswith("/api/auth/login"):
            return self.login_limiter
        
        # Register endpoint: strictest limit (3 req/min per spec)
        if path.startswith("/api/auth/register"):
            return self.register_limiter
        
        # Other auth endpoints use standard auth limits
        if path.startswith("/api/auth"):
            return self.auth_limiter
        
        # Check for path-specific limiters
        for pattern, limiter in self._path_limiters.items():
            if path.startswith(pattern):
                return limiter
        
        return self.default_limiter
    
    def _get_client_key(self, request: Request) -> str:
        """Generate a rate limit key for the client.
        
        Uses X-Forwarded-For header if available, otherwise falls back to
        direct client IP.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use first IP in chain (original client)
            return forwarded_for.split(",")[0].strip()
        
        client = request.client
        if client:
            return client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiter."""
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Get rate limiter for this path
        limiter = self._get_limiter_for_path(request.url.path)
        if not limiter:
            return await call_next(request)
        
        # Get client key
        client_key = self._get_client_key(request)
        
        # Check rate limit
        is_allowed, retry_after = limiter.check(client_key)
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded for %s on %s",
                client_key,
                request.url.path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                },
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = limiter.max_requests - len(limiter._requests[client_key])
        response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        return response
    
    def add_path_limiter(
        self,
        path_prefix: str,
        max_requests: int,
        window_seconds: int = 60,
    ):
        """Add a custom rate limiter for a path prefix.
        
        Args:
            path_prefix: Path prefix to apply the limiter to
            max_requests: Maximum requests per window
            window_seconds: Window size in seconds
        """
        self._path_limiters[path_prefix] = RateLimiter(
            max_requests=max_requests,
            window_seconds=window_seconds,
        )
    
    def reset_client(self, client_key: str):
        """Reset rate limits for a specific client."""
        self.default_limiter.reset(client_key)
        self.auth_limiter.reset(client_key)
        self.login_limiter.reset(client_key)
        self.register_limiter.reset(client_key)
        for limiter in self._path_limiters.values():
            limiter.reset(client_key)
