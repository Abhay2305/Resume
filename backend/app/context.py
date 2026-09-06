"""Request context propagation via contextvars.

Provides request-scoped data access throughout the application without
explicit parameter passing. Middleware sets context variables at request
start; services access them via getter functions.

Usage in services:
    from app.context import get_request_id, get_user_id
    request_id = get_request_id()
"""

import contextvars
from typing import Optional

# Context variables for request-scoped data
_request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)
_user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "user_id", default=None
)
_session_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "session_id", default=None
)
_endpoint: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "endpoint", default=None
)
_http_method: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "http_method", default=None
)


def get_request_id() -> Optional[str]:
    """Get current request_id from context (auto-populated by AuditMiddleware)."""
    return _request_id.get()


def get_user_id() -> Optional[str]:
    """Get current user_id from context (auto-populated by AuditContextMiddleware)."""
    return _user_id.get()


def get_session_id() -> Optional[str]:
    """Get current session_id from context (auto-populated by AuditContextMiddleware)."""
    return _session_id.get()


def set_request_id(request_id: str) -> None:
    """Set request_id in context (called by AuditMiddleware)."""
    _request_id.set(request_id)


def set_user_id(user_id: str) -> None:
    """Set user_id in context (called by AuditContextMiddleware)."""
    _user_id.set(user_id)


def set_session_id(session_id: str) -> None:
    """Set session_id in context (called by AuditContextMiddleware)."""
    _session_id.set(session_id)


def get_endpoint() -> Optional[str]:
    """Get current endpoint from context (auto-populated by AuditMiddleware)."""
    return _endpoint.get()


def set_endpoint(endpoint: str) -> None:
    """Set endpoint in context (called by AuditMiddleware)."""
    _endpoint.set(endpoint)


def get_http_method() -> Optional[str]:
    """Get current HTTP method from context (auto-populated by AuditMiddleware)."""
    return _http_method.get()


def set_http_method(http_method: str) -> None:
    """Set HTTP method in context (called by AuditMiddleware)."""
    _http_method.set(http_method)


def clear_context() -> None:
    """Clear all context variables (called at request end)."""
    _request_id.set(None)
    _user_id.set(None)
    _session_id.set(None)
    _endpoint.set(None)
    _http_method.set(None)
