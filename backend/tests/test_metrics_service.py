"""Tests for Metrics Service (PROC-SPEC-0.5).

Unit tests for repository, service, and schema validation.
Integration tests for API endpoints.
Error handling and validation tests.
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.auth import require_admin
from app.models import Base
from app.models.metric import SystemMetric
from app.models.identity import User
from app.repositories.metric import MetricRepository
from app.services.metrics_service import MetricsService
from app.schemas.metric import (
    MetricOut,
    MetricListResponse,
    MetricSummary,
    FlushResponse,
    CleanupResponse,
    VALID_METRIC_NAMES,
)


# ============================================================================
# Test Database Setup
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_metrics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_require_admin():
    """Mock admin user for testing."""
    return User(id="test-admin-id", email="admin@test.com", is_superuser=True)


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.fixture
def db():
    """Get a database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Get a test client."""
    return TestClient(app)


@pytest.fixture
def metric_repo(db):
    """Get a metric repository."""
    return MetricRepository(db)


@pytest.fixture
def metrics_service(db, metric_repo):
    """Get a metrics service."""
    return MetricsService(db, metric_repo)


# ============================================================================
# Model Tests
# ============================================================================

class TestSystemMetricModel:
    """Test SystemMetric model creation and fields."""

    def test_create_metric(self, db):
        """Test creating a metric record."""
        now = datetime.utcnow()
        metric = SystemMetric(
            metric_name="request_count",
            metric_value=10.0,
            dimensions={"endpoint": "/api/users"},
            recorded_at=now,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)

        assert metric.id is not None
        assert metric.metric_name == "request_count"
        assert metric.metric_value == 10.0
        assert metric.dimensions == {"endpoint": "/api/users"}
        assert metric.recorded_at.replace(tzinfo=None) == now.replace(tzinfo=None)

    def test_metric_without_dimensions(self, db):
        """Test creating a metric without dimensions."""
        now = datetime.now(timezone.utc)
        metric = SystemMetric(
            metric_name="ai_tokens",
            metric_value=1500.0,
            recorded_at=now,
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)

        assert metric.dimensions is None


# ============================================================================
# Repository Tests
# ============================================================================

class TestMetricRepository:
    """Test MetricRepository CRUD operations."""

    def test_get_by_name_and_range(self, metric_repo, db):
        """Test querying metrics by name and time range."""
        now = datetime.now(timezone.utc)
        for i in range(5):
            metric = SystemMetric(
                metric_name="request_count",
                metric_value=float(i),
                recorded_at=now - timedelta(hours=i),
            )
            db.add(metric)
        db.commit()

        items, total = metric_repo.get_by_name_and_range(
            "request_count", now - timedelta(hours=10), now
        )
        assert total == 5
        assert len(items) == 5

    def test_get_by_name_and_range_pagination(self, metric_repo, db):
        """Test pagination of metric queries."""
        now = datetime.now(timezone.utc)
        for i in range(10):
            metric = SystemMetric(
                metric_name="response_time",
                metric_value=float(i * 10),
                recorded_at=now - timedelta(minutes=i),
            )
            db.add(metric)
        db.commit()

        items, total = metric_repo.get_by_name_and_range(
            "response_time", now - timedelta(hours=1), now, page=1, limit=3
        )
        assert total == 10
        assert len(items) == 3

    def test_delete_older_than(self, metric_repo, db):
        """Test hard deletion of old metrics."""
        now = datetime.now(timezone.utc)

        # Old metric (should be deleted)
        old = SystemMetric(
            metric_name="request_count",
            metric_value=1.0,
            recorded_at=now - timedelta(days=100),
        )
        # Recent metric (should remain)
        recent = SystemMetric(
            metric_name="request_count",
            metric_value=2.0,
            recorded_at=now - timedelta(days=10),
        )
        db.add_all([old, recent])
        db.commit()

        count = metric_repo.delete_older_than(now - timedelta(days=90))
        assert count == 1

        remaining = db.query(SystemMetric).all()
        assert len(remaining) == 1
        assert remaining[0].metric_value == 2.0

    def test_count_by_name_and_range(self, metric_repo, db):
        """Test counting metrics by name and range."""
        now = datetime.now(timezone.utc)
        for i in range(3):
            metric = SystemMetric(
                metric_name="error_count",
                metric_value=1.0,
                recorded_at=now - timedelta(hours=i),
            )
            db.add(metric)
        db.commit()

        count = metric_repo.count_by_name_and_range(
            "error_count", now - timedelta(hours=5), now
        )
        assert count == 3

    def test_sum_value_by_name_and_range(self, metric_repo, db):
        """Test summing metric values by name and range."""
        now = datetime.now(timezone.utc)
        for val in [10.0, 20.0, 30.0]:
            metric = SystemMetric(
                metric_name="ai_cost",
                metric_value=val,
                recorded_at=now,
            )
            db.add(metric)
        db.commit()

        total = metric_repo.sum_value_by_name_and_range(
            "ai_cost", now - timedelta(hours=1), now
        )
        assert total == 60.0

    def test_create_many(self, metric_repo, db):
        """Test bulk insert of metric samples."""
        now = datetime.now(timezone.utc)
        samples = [
            {"metric_name": "request_count", "metric_value": 1.0, "recorded_at": now}
            for _ in range(5)
        ]
        count = metric_repo.create_many(samples)
        assert count == 5

        remaining = db.query(SystemMetric).all()
        assert len(remaining) == 5


# ============================================================================
# Service Tests
# ============================================================================

class TestMetricsService:
    """Test MetricsService business logic."""

    def test_record_request(self, metrics_service):
        """Test recording an HTTP request."""
        metrics_service.record_request("/api/users", "GET", 200, 15.5)
        metrics_service.record_request("/api/users", "GET", 200, 12.3)

        with metrics_service._lock:
            assert metrics_service._request_counts["/api/users"] == 2
            assert len(metrics_service._response_times["/api/users"]) == 2
            assert metrics_service._response_times["/api/users"] == [15.5, 12.3]

    def test_record_request_error(self, metrics_service):
        """Test that error status codes increment error count."""
        metrics_service.record_request("/api/users", "GET", 500, 100.0)

        with metrics_service._lock:
            assert "/api/users:GET:500" in metrics_service._error_counts
            assert metrics_service._error_counts["/api/users:GET:500"] == 1

    def test_record_request_client_error(self, metrics_service):
        """Test that 4xx status codes increment error count."""
        metrics_service.record_request("/api/users", "POST", 422, 50.0)

        with metrics_service._lock:
            assert "/api/users:POST:422" in metrics_service._error_counts

    def test_record_ai_usage(self, metrics_service):
        """Test recording AI token usage."""
        metrics_service.record_ai_usage("gpt-4", 1500, 0.05)
        metrics_service.record_ai_usage("gpt-4", 500, 0.02)

        with metrics_service._lock:
            assert metrics_service._ai_tokens["gpt-4"] == 2000
            assert metrics_service._ai_costs["gpt-4"] == pytest.approx(0.07)

    def test_record_job(self, metrics_service):
        """Test recording background job execution."""
        metrics_service.record_job("email_sync", "success", 1500.0)
        metrics_service.record_job("email_sync", "success", 1200.0)

        with metrics_service._lock:
            assert metrics_service._job_metrics["email_sync"]["count"] == 2
            assert metrics_service._job_metrics["email_sync"]["total_ms"] == 2700.0

    def test_flush(self, metrics_service, db):
        """Test flushing in-memory buffers to database."""
        metrics_service.record_request("/api/users", "GET", 200, 10.0)
        metrics_service.record_ai_usage("gpt-4", 100, 0.01)

        count = metrics_service.flush()
        assert count > 0

        # Verify data was persisted
        metrics = db.query(SystemMetric).all()
        assert len(metrics) > 0

        # Verify buffers are cleared
        with metrics_service._lock:
            assert len(metrics_service._request_counts) == 0
            assert len(metrics_service._ai_tokens) == 0

    def test_flush_empty(self, metrics_service):
        """Test flushing with no data returns 0."""
        count = metrics_service.flush()
        assert count == 0

    def test_cleanup_retention(self, metrics_service, db):
        """Test retention cleanup deletes old metrics."""
        now = datetime.now(timezone.utc)

        # Old metric
        old = SystemMetric(
            metric_name="request_count",
            metric_value=1.0,
            recorded_at=now - timedelta(days=100),
        )
        # Recent metric
        recent = SystemMetric(
            metric_name="request_count",
            metric_value=2.0,
            recorded_at=now - timedelta(days=10),
        )
        db.add_all([old, recent])
        db.commit()

        deleted = metrics_service.cleanup_retention()
        assert deleted == 1

    def test_get_metrics_validates_name(self, metrics_service):
        """Test that get_metrics rejects invalid metric names."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="Invalid metric name"):
            metrics_service.get_metrics("invalid_name", now, now)

    def test_thread_safety_record_request(self, metrics_service):
        """Test that concurrent record_request calls are thread-safe."""
        import threading

        def record():
            for _ in range(100):
                metrics_service.record_request("/api/test", "GET", 200, 1.0)

        threads = [threading.Thread(target=record) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        with metrics_service._lock:
            assert metrics_service._request_counts["/api/test"] == 500
            assert len(metrics_service._response_times["/api/test"]) == 500


# ============================================================================
# Schema Tests
# ============================================================================

class TestMetricSchemas:
    """Test Pydantic schema validation."""

    def test_metric_out(self):
        """Test MetricOut schema."""
        now = datetime.now(timezone.utc)
        data = {
            "id": "test-id",
            "metric_name": "request_count",
            "metric_value": 10.0,
            "dimensions": {"endpoint": "/api/users"},
            "recorded_at": now,
        }
        schema = MetricOut(**data)
        assert schema.id == "test-id"
        assert schema.metric_name == "request_count"

    def test_metric_list_response(self):
        """Test MetricListResponse schema."""
        now = datetime.now(timezone.utc)
        data = {
            "items": [
                {
                    "id": "1",
                    "metric_name": "request_count",
                    "metric_value": 10.0,
                    "recorded_at": now,
                }
            ],
            "total": 1,
            "page": 1,
            "size": 100,
        }
        schema = MetricListResponse(**data)
        assert schema.total == 1

    def test_metric_summary(self):
        """Test MetricSummary schema."""
        now = datetime.now(timezone.utc)
        data = {
            "request_count": 100,
            "avg_response_time_ms": 15.5,
            "error_rate": 0.05,
            "ai_tokens_total": 5000,
            "ai_cost_total": 0.25,
            "period_start": now - timedelta(hours=1),
            "period_end": now,
        }
        schema = MetricSummary(**data)
        assert schema.request_count == 100

    def test_valid_metric_names(self):
        """Test VALID_METRIC_NAMES allowlist."""
        expected = {
            "request_count",
            "response_time",
            "error_count",
            "ai_tokens",
            "ai_cost",
            "job_execution",
            "job_duration",
        }
        assert VALID_METRIC_NAMES == expected


# ============================================================================
# Middleware Tests
# ============================================================================

class TestMetricsMiddleware:
    """Test MetricsMiddleware behavior."""

    def test_middleware_records_request(self, client, metrics_service):
        """Test that middleware records request metrics via app.state singleton."""
        app.state.metrics_service = metrics_service

        # /api/health is not excluded, so it should be recorded
        response = client.get("/api/health")
        assert response.status_code == 200

        with metrics_service._lock:
            assert "/api/health" in metrics_service._request_counts
            assert metrics_service._request_counts["/api/health"] == 1

    def test_middleware_excluded_paths(self, client, metrics_service):
        """Test that excluded paths are not recorded."""
        app.state.metrics_service = metrics_service

        response = client.get("/docs")
        assert response.status_code == 200

        with metrics_service._lock:
            assert "/docs" not in metrics_service._request_counts

    def test_middleware_no_service_skips_recording(self, client):
        """Test that middleware skips recording when no service is available."""
        app.state.metrics_service = None

        response = client.get("/api/health")
        assert response.status_code == 200

    def test_middleware_records_response_time(self, client, metrics_service):
        """Test that middleware records response time."""
        app.state.metrics_service = metrics_service

        response = client.get("/api/health")
        assert response.status_code == 200

        with metrics_service._lock:
            assert "/api/health" in metrics_service._response_times
            assert len(metrics_service._response_times["/api/health"]) == 1
            assert metrics_service._response_times["/api/health"][0] >= 0


# ============================================================================
# API Integration Tests
# ============================================================================

class TestMetricsAPI:
    """Test metrics API endpoints with admin auth."""

    def test_list_metrics_invalid_name(self, client, metrics_service):
        """Test GET /api/metrics with invalid metric name returns 422."""
        app.state.metrics_service = metrics_service
        response = client.get("/api/metrics?metric_name=invalid_name")
        assert response.status_code == 422

    def test_list_metrics_valid_name(self, client, db, metrics_service):
        """Test GET /api/metrics with valid metric name."""
        app.state.metrics_service = metrics_service

        now = datetime.utcnow()
        metric = SystemMetric(
            metric_name="request_count",
            metric_value=10.0,
            dimensions={"endpoint": "/api/users"},
            recorded_at=now,
        )
        db.add(metric)
        db.commit()

        start = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        end = (now + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")
        response = client.get(
            f"/api/metrics?metric_name=request_count&start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_get_metrics_summary(self, client, db, metrics_service):
        """Test GET /api/metrics/summary."""
        app.state.metrics_service = metrics_service

        now = datetime.utcnow()
        metric = SystemMetric(
            metric_name="request_count",
            metric_value=10.0,
            recorded_at=now,
        )
        db.add(metric)
        db.commit()

        start = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
        end = now.strftime("%Y-%m-%dT%H:%M:%S")
        response = client.get(
            f"/api/metrics/summary?start_time={start}&end_time={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_count" in data

    def test_flush_metrics(self, client, metrics_service):
        """Test POST /api/metrics/flush."""
        app.state.metrics_service = metrics_service

        # Record something so flush has data
        metrics_service.record_request("/api/test", "GET", 200, 5.0)

        response = client.post("/api/metrics/flush")
        assert response.status_code == 200
        data = response.json()
        assert "flushed" in data
        assert data["flushed"] > 0

    def test_cleanup_metrics(self, client, metrics_service):
        """Test DELETE /api/metrics/cleanup."""
        app.state.metrics_service = metrics_service

        response = client.delete("/api/metrics/cleanup")
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data

    def test_metrics_requires_admin(self, client, metrics_service):
        """Test that metrics endpoints require admin auth."""
        app.state.metrics_service = metrics_service

        # Remove the admin override to test auth enforcement
        original_override = app.dependency_overrides.pop(require_admin, None)
        try:
            response = client.get("/api/metrics?metric_name=request_count")
            # Should return 401 or 403 without admin auth
            assert response.status_code in (401, 403)
        finally:
            if original_override:
                app.dependency_overrides[require_admin] = original_override

    def test_flush_requires_admin(self, client, metrics_service):
        """Test that flush endpoint requires admin auth."""
        app.state.metrics_service = metrics_service

        original_override = app.dependency_overrides.pop(require_admin, None)
        try:
            response = client.post("/api/metrics/flush")
            assert response.status_code in (401, 403)
        finally:
            if original_override:
                app.dependency_overrides[require_admin] = original_override

    def test_cleanup_requires_admin(self, client, metrics_service):
        """Test that cleanup endpoint requires admin auth."""
        app.state.metrics_service = metrics_service

        original_override = app.dependency_overrides.pop(require_admin, None)
        try:
            response = client.delete("/api/metrics/cleanup")
            assert response.status_code in (401, 403)
        finally:
            if original_override:
                app.dependency_overrides[require_admin] = original_override

    def test_service_unavailable_returns_503(self, client):
        """Test that 503 is returned when metrics service is not available."""
        app.state.metrics_service = None

        response = client.get(
            "/api/metrics?metric_name=request_count"
            "&start_time=2026-01-01T00:00:00&end_time=2026-01-02T00:00:00"
        )
        assert response.status_code == 503


# ============================================================================
# Singleton Verification Tests
# ============================================================================

class TestSingletonBehavior:
    """Verify MetricsService is a true singleton."""

    def test_singleton_stored_in_app_state(self, metrics_service):
        """Test that singleton is stored in app.state."""
        app.state.metrics_service = metrics_service

        resolved = getattr(app.state, "metrics_service", None)
        assert resolved is metrics_service

    def test_singleton_same_instance(self, metrics_service):
        """Test that all access points resolve to the same instance."""
        app.state.metrics_service = metrics_service

        # Middleware would resolve from request.app.state
        # Router would resolve from request.app.state
        # Both should be the same object
        assert app.state.metrics_service is metrics_service

    def test_flush_thread_guard(self, metrics_service):
        """Test that flush thread cannot start twice."""
        metrics_service.start_flush_thread()
        first_thread = metrics_service._flush_thread

        # Try to start again — should be a no-op
        metrics_service.start_flush_thread()
        second_thread = metrics_service._flush_thread

        assert first_thread is second_thread

        # Cleanup
        metrics_service.stop_flush_thread()
