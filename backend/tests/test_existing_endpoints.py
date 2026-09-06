"""Smoke tests for existing endpoints — Task 5.3.

Verifies that adding the pipeline router did not affect existing routers.
Tests health endpoint accessibility, router registration, and route conflicts.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the full app."""
    return TestClient(app, raise_server_exceptions=False)


# ============================================================================
# Health Endpoint Tests
# ============================================================================

class TestHealthEndpoint:
    """Verify /api/health is accessible."""

    def test_health_endpoint_accessible(self, client):
        """GET /api/health returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_live_endpoint(self, client):
        """GET /api/health/live returns 200."""
        response = client.get("/api/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"


# ============================================================================
# Router Registration Tests
# ============================================================================

class TestRouterRegistration:
    """Verify expected routers are registered in the app."""

    def _get_route_paths(self):
        """Collect all registered route paths."""
        paths = set()
        for route in app.routes:
            if hasattr(route, "path"):
                paths.add(route.path)
        return paths

    def test_all_routers_registered(self):
        """Verify core routers are registered."""
        paths = self._get_route_paths()

        expected_prefixes = [
            "/api/auth",
            "/api/health",
            "/api/resume",
            "/api/cover-letter",
            "/api/ats",
            "/api/user",
            "/api/pdf",
            "/api/v1/career",
            "/api/chat",
            "/api/opportunities",
            "/api/resume-intelligence",
            "/api/gap-analysis",
            "/api/knowledge",
            "/api/prompt-intelligence",
            "/api/ai/",
            "/api/ai-response",
            "/api/config",
            "/api/audit",
            "/api/metrics",
            "/api/errors",
            "/api/rbac",
            "/api/analytics",
            "/api/procs",
        ]

        for prefix in expected_prefixes:
            # Check if any route starts with this prefix
            matching = [p for p in paths if p.startswith(prefix)]
            assert len(matching) > 0, f"No routes found for prefix: {prefix}"

    def test_pipeline_routes_registered(self):
        """Verify pipeline routes are registered."""
        paths = self._get_route_paths()

        pipeline_routes = [
            "/api/pipeline/execute",
            "/api/pipeline/{pipeline_run_id}",
            "/api/pipeline/{pipeline_run_id}/stages",
        ]

        for route in pipeline_routes:
            assert route in paths, f"Pipeline route not found: {route}"


# ============================================================================
# Route Conflict Tests
# ============================================================================

class TestRouteConflicts:
    """Verify no duplicate or conflicting routes exist."""

    def test_no_route_conflicts(self):
        """Verify no duplicate route+method combinations."""
        seen = {}
        conflicts = []

        for route in app.routes:
            if hasattr(route, "methods") and hasattr(route, "path"):
                for method in route.methods:
                    key = (route.path, method)
                    if key in seen:
                        conflicts.append(key)
                    seen[key] = route.path

        assert len(conflicts) == 0, f"Route conflicts found: {conflicts}"

    def test_pipeline_does_not_shadow_existing(self):
        """Verify pipeline routes don't shadow existing routes."""
        # Get all non-pipeline routes
        non_pipeline_paths = []
        pipeline_paths = []

        for route in app.routes:
            if hasattr(route, "path"):
                if "/pipeline/" in route.path:
                    pipeline_paths.append(route.path)
                else:
                    non_pipeline_paths.append(route.path)

        # Verify no pipeline route matches a non-pipeline route exactly
        for p_path in pipeline_paths:
            assert p_path not in non_pipeline_paths, (
                f"Pipeline route shadows existing route: {p_path}"
            )
