"""Tests for Intelligence Pipeline Pydantic schemas.

Verifies request/response schema validation, serialization, and edge cases.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.pipeline import (
    PipelineExecuteRequest,
    PipelineRunResponse,
    PipelineStageResponse,
    PipelineRunListOut,
    PipelineRunListResponse,
)


# ============================================================================
# PipelineExecuteRequest Tests
# ============================================================================

class TestPipelineExecuteRequest:
    def test_import(self):
        assert PipelineExecuteRequest is not None

    def test_valid_minimal(self):
        req = PipelineExecuteRequest(
            resume_text="My resume content",
            opportunity_text="Job description content",
        )
        assert req.resume_text == "My resume content"
        assert req.opportunity_text == "Job description content"
        assert req.skip_validation is False
        assert req.metadata == {}

    def test_valid_with_all_fields(self):
        req = PipelineExecuteRequest(
            resume_text="resume",
            opportunity_text="job",
            skip_validation=True,
            metadata={"source": "api", "version": "1.0"},
        )
        assert req.skip_validation is True
        assert req.metadata == {"source": "api", "version": "1.0"}

    def test_missing_resume_text_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PipelineExecuteRequest(opportunity_text="job")
        assert "resume_text" in str(exc_info.value)

    def test_missing_opportunity_text_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            PipelineExecuteRequest(resume_text="resume")
        assert "opportunity_text" in str(exc_info.value)

    def test_empty_resume_text_raises(self):
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(resume_text="", opportunity_text="job")

    def test_empty_opportunity_text_raises(self):
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(resume_text="resume", opportunity_text="")

    def test_whitespace_only_resume_text_passes(self):
        req = PipelineExecuteRequest(
            resume_text="   ",
            opportunity_text="job",
        )
        assert req.resume_text == "   "

    def test_user_id_not_in_schema(self):
        req = PipelineExecuteRequest(resume_text="r", opportunity_text="o")
        assert not hasattr(req, "user_id")


# ============================================================================
# PipelineStageResponse Tests
# ============================================================================

class TestPipelineStageResponse:
    def test_import(self):
        assert PipelineStageResponse is not None

    def test_valid_minimal(self):
        resp = PipelineStageResponse(
            stage_name="resume_intelligence",
            stage_order=1,
            status="completed",
        )
        assert resp.stage_name == "resume_intelligence"
        assert resp.stage_order == 1
        assert resp.status == "completed"
        assert resp.entity_id is None
        assert resp.latency_ms == 0.0
        assert resp.error is None
        assert resp.metadata == {}

    def test_valid_with_all_fields(self):
        resp = PipelineStageResponse(
            stage_name="knowledge_intelligence",
            stage_order=3,
            status="failed",
            entity_id="550e8400-e29b-41d4-a716-446655440000",
            latency_ms=1234.56,
            error="Service unavailable",
            metadata={"retry_count": 3},
        )
        assert resp.entity_id == "550e8400-e29b-41d4-a716-446655440000"
        assert resp.latency_ms == 1234.56
        assert resp.error == "Service unavailable"

    def test_skip_validation_status(self):
        resp = PipelineStageResponse(
            stage_name="ai_response_intelligence",
            stage_order=7,
            status="skipped",
        )
        assert resp.status == "skipped"

    def test_missing_stage_name_raises(self):
        with pytest.raises(ValidationError):
            PipelineStageResponse(stage_order=1, status="completed")

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            PipelineStageResponse(stage_name="test", stage_order=1)


# ============================================================================
# PipelineRunResponse Tests
# ============================================================================

class TestPipelineRunResponse:
    def test_import(self):
        assert PipelineRunResponse is not None

    def test_valid_minimal(self):
        resp = PipelineRunResponse(
            pipeline_run_id="550e8400-e29b-41d4-a716-446655440000",
            status="completed",
            stages=[],
        )
        assert resp.pipeline_run_id == "550e8400-e29b-41d4-a716-446655440000"
        assert resp.status == "completed"
        assert resp.stages == []
        assert resp.resume_profile_id is None
        assert resp.opportunity_id is None
        assert resp.gap_analysis_id is None
        assert resp.knowledge_retrieval_id is None
        assert resp.prompt_package_id is None
        assert resp.ai_execution_id is None
        assert resp.ai_validation_id is None
        assert resp.ai_response is None
        assert resp.validation_result is None
        assert resp.error is None
        assert resp.total_latency_ms == 0.0

    def test_valid_with_all_fields(self):
        resp = PipelineRunResponse(
            pipeline_run_id="550e8400-e29b-41d4-a716-446655440000",
            status="failed",
            stages=[
                PipelineStageResponse(
                    stage_name="resume_intelligence",
                    stage_order=1,
                    status="completed",
                ),
                PipelineStageResponse(
                    stage_name="opportunity_intelligence",
                    stage_order=2,
                    status="failed",
                    error="Parse error",
                ),
            ],
            resume_profile_id="res-001",
            opportunity_id="opp-001",
            error="Stage 2 failed",
            total_latency_ms=5432.1,
        )
        assert len(resp.stages) == 2
        assert resp.stages[1].error == "Parse error"
        assert resp.error == "Stage 2 failed"

    def test_serialization_roundtrip(self):
        resp = PipelineRunResponse(
            pipeline_run_id="run-123",
            status="completed",
            stages=[],
            total_latency_ms=100.0,
        )
        data = resp.model_dump()
        assert data["pipeline_run_id"] == "run-123"
        assert data["status"] == "completed"
        assert data["total_latency_ms"] == 100.0
        resp2 = PipelineRunResponse(**data)
        assert resp2.pipeline_run_id == resp.pipeline_run_id

    def test_missing_pipeline_run_id_raises(self):
        with pytest.raises(ValidationError):
            PipelineRunResponse(status="completed", stages=[])

    def test_missing_status_raises(self):
        with pytest.raises(ValidationError):
            PipelineRunResponse(pipeline_run_id="run-1", stages=[])


# ============================================================================
# PipelineRunListOut Tests
# ============================================================================

class TestPipelineRunListOut:
    def test_import(self):
        assert PipelineRunListOut is not None

    def test_valid(self):
        item = PipelineRunListOut(
            id="550e8400-e29b-41d4-a716-446655440000",
            status="completed",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert item.id == "550e8400-e29b-41d4-a716-446655440000"
        assert item.status == "completed"

    def test_with_preview(self):
        item = PipelineRunListOut(
            id="run-1",
            status="completed",
            resume_text_preview="First 100 chars...",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert item.resume_text_preview == "First 100 chars..."


# ============================================================================
# PipelineRunListResponse Tests
# ============================================================================

class TestPipelineRunListResponse:
    def test_import(self):
        assert PipelineRunListResponse is not None

    def test_valid(self):
        resp = PipelineRunListResponse(
            items=[],
            total=0,
            page=1,
            size=10,
        )
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 10

    def test_with_items(self):
        resp = PipelineRunListResponse(
            items=[
                PipelineRunListOut(
                    id="run-1",
                    status="completed",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
            ],
            total=1,
            page=1,
            size=10,
        )
        assert len(resp.items) == 1
