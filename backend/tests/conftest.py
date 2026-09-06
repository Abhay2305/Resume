"""Shared test fixtures and setup."""
import pytest


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the global rate limiter state before each test.

    The RateLimitMiddleware uses in-memory sliding window counters that
    persist across tests when the same TestClient (and therefore the same
    middleware instance) is reused.  This fixture clears all counters so
    that each test starts with a fresh budget.
    """
    from app.main import app
    from app.middleware.rate_limit import RateLimitMiddleware

    stack = getattr(app, "middleware_stack", None)
    if stack is not None:
        current = stack
        while current is not None:
            if type(current).__name__ == "RateLimitMiddleware" and hasattr(current, "reset_client"):
                current.reset_client("testclient")
                current.reset_client("unknown")
                break
            inner = getattr(current, "app", None)
            if inner is current or inner is None:
                break
            current = inner
