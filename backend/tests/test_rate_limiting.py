"""Tests for rate limiting middleware.

Tests per-endpoint rate limits:
- Login: 5 requests/minute/IP (SPEC-0.1 NFR)
- Register: 3 requests/minute/IP (SPEC-0.1 NFR)
- Default: 100 requests/minute/IP
"""
import time
import pytest

pytestmark = pytest.mark.rate_limit
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.rate_limit import RateLimiter, RateLimitMiddleware


def _create_test_app():
    """Create a minimal test app with rate limiting."""
    test_app = FastAPI()
    test_app.add_middleware(
        RateLimitMiddleware,
        default_max_requests=100,
        default_window_seconds=60,
        auth_max_requests=10,
        auth_window_seconds=60,
        login_max_requests=5,
        login_window_seconds=60,
        register_max_requests=3,
        register_window_seconds=60,
    )

    @test_app.get("/health")
    async def health():
        return {"status": "ok"}

    @test_app.post("/api/auth/login")
    async def login():
        return {"status": "ok"}

    @test_app.post("/api/auth/register")
    async def register():
        return {"status": "ok"}

    @test_app.get("/api/auth/me")
    async def me():
        return {"status": "ok"}

    return test_app


class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            is_allowed, retry_after = limiter.check("test-key")
            assert is_allowed is True
            assert retry_after is None

    def test_blocks_requests_over_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.check("test-key")
        
        is_allowed, retry_after = limiter.check("test-key")
        assert is_allowed is False
        assert retry_after is not None
        assert retry_after > 0

    def test_different_keys_independent(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("key1")
        limiter.check("key1")
        
        is_allowed, _ = limiter.check("key1")
        assert is_allowed is False
        
        is_allowed, _ = limiter.check("key2")
        assert is_allowed is True

    def test_reset_clears_limit(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("key1")
        limiter.check("key1")
        
        is_allowed, _ = limiter.check("key1")
        assert is_allowed is False
        
        limiter.reset("key1")
        is_allowed, _ = limiter.check("key1")
        assert is_allowed is True


class TestRateLimitMiddleware:
    def test_login_rate_limit(self):
        """Login endpoint: 5 requests per minute."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        for _ in range(5):
            client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
        
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    def test_register_rate_limit(self):
        """Register endpoint: 3 requests per minute."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        for i in range(3):
            client.post("/api/auth/register", json={
                "email": f"user{i}@example.com",
                "password": "StrongPass123",
                "full_name": f"User {i}",
            })
        
        response = client.post("/api/auth/register", json={
            "email": "user3@example.com",
            "password": "StrongPass123",
            "full_name": "User 3",
        })
        assert response.status_code == 429
        assert "Too many requests" in response.json()["detail"]

    def test_rate_limit_headers_present(self):
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/api/auth/me")
        assert "X-RateLimit-Limit" in response.headers

    def test_429_response_includes_retry_after(self):
        """429 responses must include Retry-After header."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        for _ in range(5):
            client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
        
        response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) > 0

    def test_different_endpoints_independent_limits(self):
        """Login and register have separate rate limits."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        # Exhaust login limit (5)
        for _ in range(5):
            client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong"})

        # Register should still work (separate limiter, 3 max)
        for i in range(3):
            response = client.post("/api/auth/register", json={
                "email": f"newuser{i}@example.com",
                "password": "StrongPass123",
                "full_name": f"New User {i}",
            })
            assert response.status_code == 200

    def test_health_endpoint_skips_rate_limiting(self):
        """Health endpoint should not be rate limited."""
        app = _create_test_app()
        client = TestClient(app, raise_server_exceptions=False)

        for _ in range(200):
            response = client.get("/health")
            assert response.status_code == 200
