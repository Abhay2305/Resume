"""Tests for Pipeline Intelligence Router — Task 5.1.

Verifies API endpoints for pipeline execution, status retrieval,
and stage information using mocked services.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.pipeline import router
from app.auth import require_auth
from app.database import get_db
from app.schemas.pipeline import PipelineExecuteRequest, PipelineRunResponse, PipelineStageResponse
from app.services.intelligence_pipeline.types import PipelineResult, StageResult


# ============================================================================
# Test Fixtures
# ============================================================================

def _make_mock_user(user_id="user-1"):
    """Create a mock authenticated user."""
    user = MagicMock()
    user.id = user_id
    return user


def _make_pipeline_result(status="completed", stages=None):
    """Create a mock PipelineResult."""
    if stages is None:
        stages = [
            StageResult(
                stage_name="resume_intelligence",
                stage_order=1,
                status="completed",
                entity_id="rp-1",
                latency_ms=1200.0,
            ),
            StageResult(
                stage_name="opportunity_intelligence",
                stage_order=2,
                status="completed",
                entity_id="opp-1",
                latency_ms=800.0,
            ),
            StageResult(
                stage_name="gap_analysis",
                stage_order=3,
                status="completed",
                entity_id="ga-1",
                latency_ms=150.0,
            ),
            StageResult(
                stage_name="knowledge_intelligence",
                stage_order=4,
                status="completed",
                entity_id="kr-1",
                latency_ms=200.0,
            ),
            StageResult(
                stage_name="prompt_intelligence",
                stage_order=5,
                status="completed",
                entity_id="pp-1",
                latency_ms=50.0,
            ),
            StageResult(
                stage_name="ai_execution",
                stage_order=6,
                status="completed",
                entity_id="ae-1",
                latency_ms=3500.0,
            ),
            StageResult(
                stage_name="ai_response_intelligence",
                stage_order=7,
                status="completed",
                entity_id="av-1",
                latency_ms=300.0,
            ),
        ]

    return PipelineResult(
        pipeline_run_id="run-1",
        status=status,
        stages=stages,
        resume_profile_id="rp-1",
        opportunity_id="opp-1",
        gap_analysis_id="ga-1",
        knowledge_retrieval_id="kr-1",
        prompt_package_id="pp-1",
        ai_execution_id="ae-1",
        ai_validation_id="av-1",
        total_latency_ms=6200.0,
    )


# ============================================================================
# Test Pipeline Router
# ============================================================================

class TestPipelineRouter:
    """Task 5.1: Pipeline API endpoint tests."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_execute_pipeline_endpoint(self):
        """POST /pipeline/execute with authentication succeeds."""
        mock_user = _make_mock_user("user-1")

        with patch("app.routers.pipeline._build_service") as mock_build:
            mock_service = MagicMock()
            mock_service.execute_pipeline.return_value = _make_pipeline_result()
            mock_build.return_value = mock_service

            self.app.dependency_overrides[require_auth] = lambda: mock_user
            self.app.dependency_overrides[get_db] = lambda: MagicMock()

            response = self.client.post(
                "/pipeline/execute",
                json={
                    "resume_text": "John Doe, Software Engineer",
                    "opportunity_text": "Senior React Developer at Netflix",
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["pipeline_run_id"] == "run-1"
            assert data["status"] == "completed"
            assert len(data["stages"]) == 7

            self.app.dependency_overrides.clear()

    def test_execute_pipeline_requires_auth(self):
        """POST /pipeline/execute without authentication returns 401."""
        self.app.dependency_overrides[get_db] = lambda: MagicMock()

        response = self.client.post(
            "/pipeline/execute",
            json={
                "resume_text": "John Doe",
                "opportunity_text": "Software Engineer",
            },
        )

        assert response.status_code == 401
        self.app.dependency_overrides.clear()

    def test_get_pipeline_status_endpoint(self):
        """GET /pipeline/{id} with authentication succeeds."""
        mock_user = _make_mock_user("user-1")
        mock_run = MagicMock()
        mock_run.user_id = "user-1"

        with patch("app.routers.pipeline._build_service") as mock_build:
            mock_service = MagicMock()
            mock_service.get_pipeline_status.return_value = _make_pipeline_result()
            mock_build.return_value = mock_service

            with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
                mock_repo = MockRepo.return_value
                mock_repo.get_by_id.return_value = mock_run

                self.app.dependency_overrides[require_auth] = lambda: mock_user
                self.app.dependency_overrides[get_db] = lambda: MagicMock()

                response = self.client.get("/pipeline/run-1")

                assert response.status_code == 200
                data = response.json()
                assert data["pipeline_run_id"] == "run-1"
                assert data["status"] == "completed"

                self.app.dependency_overrides.clear()

    def test_get_pipeline_status_not_found(self):
        """GET /pipeline/{id} with nonexistent run returns 404."""
        mock_user = _make_mock_user("user-1")

        with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id.return_value = None

            self.app.dependency_overrides[require_auth] = lambda: mock_user
            self.app.dependency_overrides[get_db] = lambda: MagicMock()

            response = self.client.get("/pipeline/nonexistent")

            assert response.status_code == 404
            self.app.dependency_overrides.clear()

    def test_get_pipeline_status_forbidden(self):
        """GET /pipeline/{id} for another user's pipeline returns 403."""
        mock_user = _make_mock_user("user-2")
        mock_run = MagicMock()
        mock_run.user_id = "user-1"

        with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id.return_value = mock_run

            self.app.dependency_overrides[require_auth] = lambda: mock_user
            self.app.dependency_overrides[get_db] = lambda: MagicMock()

            response = self.client.get("/pipeline/run-1")

            assert response.status_code == 403
            self.app.dependency_overrides.clear()

    def test_get_pipeline_stages_endpoint(self):
        """GET /pipeline/{id}/stages returns only stages."""
        mock_user = _make_mock_user("user-1")
        mock_run = MagicMock()
        mock_run.user_id = "user-1"

        with patch("app.routers.pipeline._build_service") as mock_build:
            mock_service = MagicMock()
            mock_service.get_pipeline_status.return_value = _make_pipeline_result()
            mock_build.return_value = mock_service

            with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
                mock_repo = MockRepo.return_value
                mock_repo.get_by_id.return_value = mock_run

                self.app.dependency_overrides[require_auth] = lambda: mock_user
                self.app.dependency_overrides[get_db] = lambda: MagicMock()

                response = self.client.get("/pipeline/run-1/stages")

                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
                assert len(data) == 7
                assert data[0]["stage_name"] == "resume_intelligence"

                self.app.dependency_overrides.clear()

    def test_get_pipeline_stages_not_found(self):
        """GET /pipeline/{id}/stages with nonexistent run returns 404."""
        mock_user = _make_mock_user("user-1")

        with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id.return_value = None

            self.app.dependency_overrides[require_auth] = lambda: mock_user
            self.app.dependency_overrides[get_db] = lambda: MagicMock()

            response = self.client.get("/pipeline/nonexistent/stages")

            assert response.status_code == 404
            self.app.dependency_overrides.clear()

    def test_get_pipeline_stages_forbidden(self):
        """GET /pipeline/{id}/stages for another user's pipeline returns 403."""
        mock_user = _make_mock_user("user-2")
        mock_run = MagicMock()
        mock_run.user_id = "user-1"

        with patch("app.routers.pipeline.PipelineRunRepository") as MockRepo:
            mock_repo = MockRepo.return_value
            mock_repo.get_by_id.return_value = mock_run

            self.app.dependency_overrides[require_auth] = lambda: mock_user
            self.app.dependency_overrides[get_db] = lambda: MagicMock()

            response = self.client.get("/pipeline/run-1/stages")

            assert response.status_code == 403
            self.app.dependency_overrides.clear()
