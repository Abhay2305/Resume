"""Tests for Intelligence Pipeline type definitions.

Verifies that PipelineRequest, PipelineResult, and StageResult
are importable and have correct default values.
"""
import pytest
from app.services.intelligence_pipeline.types import (
    PipelineRequest,
    PipelineResult,
    StageResult,
)


class TestPipelineRequest:
    def test_import(self):
        assert PipelineRequest is not None

    def test_required_fields(self):
        req = PipelineRequest(resume_text="resume", opportunity_text="job")
        assert req.resume_text == "resume"
        assert req.opportunity_text == "job"

    def test_defaults(self):
        req = PipelineRequest(resume_text="r", opportunity_text="o")
        assert req.skip_validation is False
        assert req.metadata == {}

    def test_custom_values(self):
        req = PipelineRequest(
            resume_text="r",
            opportunity_text="o",
            skip_validation=True,
            metadata={"key": "val"},
        )
        assert req.skip_validation is True
        assert req.metadata == {"key": "val"}

    def test_user_id_not_in_request(self):
        req = PipelineRequest(resume_text="r", opportunity_text="o")
        assert not hasattr(req, "user_id")


class TestStageResult:
    def test_import(self):
        assert StageResult is not None

    def test_required_fields(self):
        sr = StageResult(stage_name="test", stage_order=1, status="pending")
        assert sr.stage_name == "test"
        assert sr.stage_order == 1
        assert sr.status == "pending"

    def test_defaults(self):
        sr = StageResult(stage_name="test", stage_order=1, status="pending")
        assert sr.entity_id is None
        assert sr.latency_ms == 0.0
        assert sr.error is None
        assert sr.metadata == {}

    def test_failed_property(self):
        sr = StageResult(stage_name="test", stage_order=1, status="failed")
        assert sr.failed is True
        assert sr.completed is False

    def test_completed_property(self):
        sr = StageResult(stage_name="test", stage_order=1, status="completed")
        assert sr.failed is False
        assert sr.completed is True

    def test_skipped_status(self):
        sr = StageResult(stage_name="test", stage_order=1, status="skipped")
        assert sr.status == "skipped"
        assert sr.failed is False
        assert sr.completed is False


class TestPipelineResult:
    def test_import(self):
        assert PipelineResult is not None

    def test_required_fields(self):
        pr = PipelineResult(
            pipeline_run_id="run_1",
            status="completed",
            stages=[],
        )
        assert pr.pipeline_run_id == "run_1"
        assert pr.status == "completed"
        assert pr.stages == []

    def test_defaults(self):
        pr = PipelineResult(
            pipeline_run_id="run_1",
            status="completed",
            stages=[],
        )
        assert pr.resume_profile_id is None
        assert pr.opportunity_id is None
        assert pr.gap_analysis_id is None
        assert pr.knowledge_retrieval_id is None
        assert pr.prompt_package_id is None
        assert pr.ai_execution_id is None
        assert pr.ai_validation_id is None
        assert pr.ai_response is None
        assert pr.validation_result is None
        assert pr.error is None
        assert pr.total_latency_ms == 0.0

    def test_all_fields_populated(self):
        stages = [
            StageResult(stage_name="s1", stage_order=1, status="completed"),
            StageResult(stage_name="s2", stage_order=2, status="failed"),
        ]
        pr = PipelineResult(
            pipeline_run_id="run_1",
            status="failed",
            stages=stages,
            resume_profile_id="rp_1",
            opportunity_id="opp_1",
            gap_analysis_id="ga_1",
            knowledge_retrieval_id="kr_1",
            prompt_package_id="pp_1",
            ai_execution_id="ae_1",
            ai_validation_id="av_1",
            ai_response={"summary": "..."},
            validation_result={"status": "approved"},
            error="Stage 2 failed",
            total_latency_ms=1500.0,
        )
        assert pr.resume_profile_id == "rp_1"
        assert pr.opportunity_id == "opp_1"
        assert pr.gap_analysis_id == "ga_1"
        assert pr.knowledge_retrieval_id == "kr_1"
        assert pr.prompt_package_id == "pp_1"
        assert pr.ai_execution_id == "ae_1"
        assert pr.ai_validation_id == "av_1"
        assert pr.ai_response == {"summary": "..."}
        assert pr.validation_result == {"status": "approved"}
        assert pr.error == "Stage 2 failed"
        assert pr.total_latency_ms == 1500.0
        assert len(pr.stages) == 2
