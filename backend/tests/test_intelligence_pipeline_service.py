"""Tests for Intelligence Pipeline Service — Task 2.1 Core.

Verifies service instantiation, pipeline creation, stage execution tracking,
and PipelineResult construction using mocked dependencies.
"""
import time
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime

from app.models.pipeline import PipelineRun, PipelineStage
from app.repositories.pipeline import PipelineRunRepository, PipelineStageRepository
from app.services.intelligence_pipeline.service import (
    IntelligencePipelineService,
    STAGE_NAMES,
    REQUIRED_STAGES,
    NON_FATAL_STAGES,
)
from app.services.intelligence_pipeline.types import (
    PipelineRequest,
    PipelineResult,
    StageResult,
)


# ============================================================================
# Helpers
# ============================================================================

def _make_mock_service(name="test_service"):
    """Create a mock service with a name attribute."""
    mock = MagicMock()
    mock.name = name
    return mock


def _make_mock_repo(return_run=None, return_stages=None):
    """Create a mock repository."""
    mock = MagicMock()
    if return_run is not None:
        mock.create.return_value = return_run
    if return_stages is not None:
        mock.create_batch.return_value = return_stages
    return mock


def _make_pipeline_run(id="run-123", user_id="user-1"):
    """Create a mock PipelineRun."""
    run = MagicMock(spec=PipelineRun)
    run.id = id
    run.user_id = user_id
    run.status = "running"
    run.resume_text = "resume content"
    run.opportunity_text = "job description"
    run.resume_profile_id = None
    run.opportunity_id = None
    run.gap_analysis_id = None
    run.knowledge_retrieval_id = None
    run.prompt_package_id = None
    run.ai_execution_id = None
    run.ai_validation_id = None
    return run


def _make_pipeline_stage(order, name=None, id=None):
    """Create a mock PipelineStage."""
    if name is None:
        name = STAGE_NAMES[order - 1]
    if id is None:
        id = f"stage-{order}"
    stage = MagicMock(spec=PipelineStage)
    stage.id = id
    stage.stage_name = name
    stage.stage_order = order
    stage.status = "pending"
    stage.entity_id = None
    stage.latency_ms = 0.0
    stage.error_message = None
    stage.started_at = None
    stage.completed_at = None
    return stage


# ============================================================================
# TestStageNames
# ============================================================================

class TestStageNames:
    def test_stage_names_count(self):
        assert len(STAGE_NAMES) == 7

    def test_stage_names_values(self):
        assert STAGE_NAMES == [
            "resume_intelligence",
            "opportunity_intelligence",
            "gap_analysis",
            "knowledge_intelligence",
            "prompt_intelligence",
            "ai_execution",
            "ai_response_intelligence",
        ]

    def test_required_stages(self):
        assert REQUIRED_STAGES == {1, 2, 3, 5, 6}

    def test_non_fatal_stages(self):
        assert NON_FATAL_STAGES == {4, 7}


# ============================================================================
# TestServiceInstantiation
# ============================================================================

class TestServiceInstantiation:
    def test_all_dependencies_injected(self):
        db = MagicMock()
        resume_svc = _make_mock_service("resume")
        opp_svc = _make_mock_service("opportunity")
        gap_svc = _make_mock_service("gap")
        knowledge_svc = _make_mock_service("knowledge")
        prompt_svc = _make_mock_service("prompt")
        execution_svc = _make_mock_service("execution")
        validation_svc = _make_mock_service("validation")
        run_repo = MagicMock(spec=PipelineRunRepository)
        stage_repo = MagicMock(spec=PipelineStageRepository)

        service = IntelligencePipelineService(
            db=db,
            resume_intelligence_service=resume_svc,
            opportunity_service=opp_svc,
            gap_analysis_service=gap_svc,
            knowledge_intelligence_service=knowledge_svc,
            prompt_intelligence_service=prompt_svc,
            ai_execution_service=execution_svc,
            ai_response_intelligence_service=validation_svc,
            pipeline_run_repo=run_repo,
            pipeline_stage_repo=stage_repo,
        )

        assert service.db is db
        assert service.resume_intelligence_service is resume_svc
        assert service.opportunity_service is opp_svc
        assert service.gap_analysis_service is gap_svc
        assert service.knowledge_intelligence_service is knowledge_svc
        assert service.prompt_intelligence_service is prompt_svc
        assert service.ai_execution_service is execution_svc
        assert service.ai_response_intelligence_service is validation_svc
        assert service.pipeline_run_repo is run_repo
        assert service.pipeline_stage_repo is stage_repo

    def test_no_direct_instantiation(self):
        """Verify service does not instantiate dependencies internally."""
        db = MagicMock()
        run_repo = MagicMock(spec=PipelineRunRepository)
        stage_repo = MagicMock(spec=PipelineStageRepository)

        # All other services are MagicMock (not real implementations)
        service = IntelligencePipelineService(
            db=db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=run_repo,
            pipeline_stage_repo=stage_repo,
        )

        assert service is not None


# ============================================================================
# TestExecutePipeline
# ============================================================================

class TestExecutePipeline:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run()
        self.stages = [_make_pipeline_stage(i + 1) for i in range(7)]

        self.run_repo = MagicMock(spec=PipelineRunRepository)
        self.run_repo.create.return_value = self.run

        self.stage_repo = MagicMock(spec=PipelineStageRepository)
        self.stage_repo.create_batch.return_value = self.stages

        # Mock all services
        self.resume_svc = MagicMock()
        self.opp_svc = MagicMock()
        self.gap_svc = MagicMock()
        self.knowledge_svc = MagicMock()
        self.prompt_svc = MagicMock()
        self.execution_svc = MagicMock()
        self.validation_svc = MagicMock()

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=self.resume_svc,
            opportunity_service=self.opp_svc,
            gap_analysis_service=self.gap_svc,
            knowledge_intelligence_service=self.knowledge_svc,
            prompt_intelligence_service=self.prompt_svc,
            ai_execution_service=self.execution_svc,
            ai_response_intelligence_service=self.validation_svc,
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_creates_pipeline_run(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Make all stage stubs succeed (by not raising)
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        self.run_repo.create.assert_called_once()
        call_args = self.run_repo.create.call_args[0][0]
        assert call_args["user_id"] == "user-1"
        assert call_args["status"] == "running"
        assert call_args["resume_text"] == "resume"
        assert call_args["opportunity_text"] == "job"

    def test_creates_seven_stages(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        self.stage_repo.create_batch.assert_called_once()
        stage_data = self.stage_repo.create_batch.call_args[0][0]
        assert len(stage_data) == 7
        for i, data in enumerate(stage_data):
            assert data["pipeline_run_id"] == self.run.id
            assert data["stage_name"] == STAGE_NAMES[i]
            assert data["stage_order"] == i + 1
            assert data["status"] == "pending"

    def test_returns_pipeline_result(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert isinstance(result, PipelineResult)
        assert result.pipeline_run_id == self.run.id
        assert result.status == "completed"
        assert len(result.stages) == 7

    def test_returns_failed_status_on_required_stage_failure(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Stage 1 (required) fails
        self.service._stage_resume_intelligence = MagicMock(
            side_effect=ValueError("Stage 1 failed")
        )

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_returns_failed_status_on_gap_analysis_failure(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Stage 1 succeeds
        self.service._stage_resume_intelligence = MagicMock()
        # Stage 2 succeeds
        self.service._stage_opportunity = MagicMock()
        # Stage 3 (required) fails
        self.service._stage_gap_analysis = MagicMock(
            side_effect=ValueError("Gap analysis failed")
        )

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"

    def test_returns_completed_when_knowledge_stage_fails(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Stages 1-3 succeed
        self.service._stage_resume_intelligence = MagicMock()
        self.service._stage_opportunity = MagicMock()
        self.service._stage_gap_analysis = MagicMock()
        # Stage 4 (non-fatal) fails
        self.service._stage_knowledge = MagicMock(
            side_effect=ValueError("Knowledge failed")
        )
        # Stages 5-7 succeed
        self.service._stage_prompt = MagicMock()
        self.service._stage_execution = MagicMock()
        self.service._stage_validation = MagicMock()

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 4 failure is non-fatal, pipeline completes
        assert result.status == "completed"

    def test_returns_completed_when_validation_stage_fails(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Stages 1-6 succeed
        self.service._stage_resume_intelligence = MagicMock()
        self.service._stage_opportunity = MagicMock()
        self.service._stage_gap_analysis = MagicMock()
        self.service._stage_knowledge = MagicMock()
        self.service._stage_prompt = MagicMock()
        self.service._stage_execution = MagicMock()
        # Stage 7 (non-fatal) fails
        self.service._stage_validation = MagicMock(
            side_effect=ValueError("Validation failed")
        )

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 7 failure is non-fatal, pipeline completes
        assert result.status == "completed"

    def test_skip_validation_skips_stage_7(self):
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
            skip_validation=True,
        )

        # Mock all stage functions including validation
        validation_mock = MagicMock()
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 7 should not be called (skip_validation=True)
        self.service._stage_validation.assert_not_called()
        # Stage 7 should be marked as skipped
        assert self.stages[6].status == "skipped"


# ============================================================================
# TestExecuteStage
# ============================================================================

class TestExecuteStage:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run()
        self.stage = _make_pipeline_stage(1)

        self.run_repo = MagicMock(spec=PipelineRunRepository)
        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_marks_stage_running(self):
        stage_func = MagicMock()

        self.service._execute_stage(self.run, self.stage, stage_func)

        self.stage_repo.update_status.assert_any_call(
            self.stage.id, "running"
        )

    def test_marks_stage_completed_on_success(self):
        stage_func = MagicMock()

        result = self.service._execute_stage(self.run, self.stage, stage_func)

        self.stage_repo.update_status.assert_any_call(
            self.stage.id, "completed", latency_ms=pytest.approx(0, abs=100)
        )
        assert result.status == "completed"

    def test_marks_stage_failed_on_exception_for_required_stage(self):
        """Required stage (order 1) re-raises exception after marking failed."""
        self.stage.stage_order = 1
        stage_func = MagicMock(side_effect=ValueError("Stage failed"))

        with pytest.raises(ValueError, match="Stage failed"):
            self.service._execute_stage(self.run, self.stage, stage_func)

        # Stage should be marked failed before re-raising
        self.stage_repo.update_status.assert_any_call(
            self.stage.id, "failed", latency_ms=pytest.approx(0, abs=100),
            error_message="Stage failed"
        )

    def test_marks_stage_failed_on_exception_for_non_fatal_stage(self):
        """Non-fatal stage (order 4) returns StageResult instead of raising."""
        self.stage.stage_order = 4
        stage_func = MagicMock(side_effect=ValueError("Stage failed"))

        result = self.service._execute_stage(self.run, self.stage, stage_func)

        assert result.status == "failed"
        assert result.error == "Stage failed"

    def test_records_latency(self):
        stage_func = MagicMock()

        result = self.service._execute_stage(self.run, self.stage, stage_func)

        assert result.latency_ms >= 0

    def test_non_fatal_stage_does_not_raise(self):
        """Non-fatal stage (order 4) should not raise exception."""
        self.stage.stage_order = 4
        stage_func = MagicMock(side_effect=ValueError("Knowledge failed"))

        # Should not raise
        result = self.service._execute_stage(self.run, self.stage, stage_func)

        assert result.status == "failed"
        assert result.error == "Knowledge failed"

    def test_required_stage_raises_exception(self):
        """Required stage (order 1) should raise exception."""
        self.stage.stage_order = 1
        stage_func = MagicMock(side_effect=ValueError("Stage failed"))

        with pytest.raises(ValueError, match="Stage failed"):
            self.service._execute_stage(self.run, self.stage, stage_func)

    def test_returns_stage_result(self):
        stage_func = MagicMock()

        result = self.service._execute_stage(self.run, self.stage, stage_func)

        assert isinstance(result, StageResult)
        assert result.stage_name == self.stage.stage_name
        assert result.stage_order == self.stage.stage_order


# ============================================================================
# TestBuildResult
# ============================================================================

class TestBuildResult:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run()
        self.stages = [_make_pipeline_stage(i + 1) for i in range(7)]

        self.run_repo = MagicMock(spec=PipelineRunRepository)
        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_builds_completed_result(self):
        result = self.service._build_result(
            self.run, self.stages, "completed", time.time()
        )

        assert isinstance(result, PipelineResult)
        assert result.status == "completed"
        assert result.pipeline_run_id == self.run.id

    def test_builds_failed_result_with_error(self):
        result = self.service._build_result(
            self.run, self.stages, "failed", time.time(), error="Stage failed"
        )

        assert result.status == "failed"
        assert result.error == "Stage failed"

    def test_includes_entity_ids(self):
        self.run.resume_profile_id = "rp-1"
        self.run.opportunity_id = "opp-1"
        self.run.gap_analysis_id = "ga-1"
        self.run.knowledge_retrieval_id = "kr-1"
        self.run.prompt_package_id = "pp-1"
        self.run.ai_execution_id = "ae-1"
        self.run.ai_validation_id = "av-1"

        result = self.service._build_result(
            self.run, self.stages, "completed", time.time()
        )

        assert result.resume_profile_id == "rp-1"
        assert result.opportunity_id == "opp-1"
        assert result.gap_analysis_id == "ga-1"
        assert result.knowledge_retrieval_id == "kr-1"
        assert result.prompt_package_id == "pp-1"
        assert result.ai_execution_id == "ae-1"
        assert result.ai_validation_id == "av-1"

    def test_updates_run_status(self):
        self.service._build_result(
            self.run, self.stages, "completed", time.time()
        )

        self.run_repo.update_status.assert_called_once()
        call_args = self.run_repo.update_status.call_args
        assert call_args[0][0] == self.run.id
        assert call_args[0][1] == "completed"

    def test_builds_stage_results(self):
        result = self.service._build_result(
            self.run, self.stages, "completed", time.time()
        )

        assert len(result.stages) == 7
        for i, sr in enumerate(result.stages):
            assert isinstance(sr, StageResult)
            assert sr.stage_name == STAGE_NAMES[i]
            assert sr.stage_order == i + 1


# ============================================================================
# TestStageStubs
# ============================================================================

class TestStageStubs:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run()
        self.stage = _make_pipeline_stage(1)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=MagicMock(),
        )



# ============================================================================
# TestStage1ResumeIntelligence
# ============================================================================

class TestStage1ResumeIntelligence:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-123")
        self.run.resume_text = "John Doe, Python developer"
        self.stage = _make_pipeline_stage(1)

        # Mock profile returned by create_profile
        self.mock_profile = MagicMock()
        self.mock_profile.id = "profile-abc-123"

        self.resume_svc = MagicMock()
        self.resume_svc.create_profile.return_value = self.mock_profile
        self.resume_svc.trigger_parse.return_value = self.mock_profile

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=self.resume_svc,
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_create_profile_called_with_correct_args(self):
        self.service._stage_resume_intelligence(self.run, self.stage)

        self.resume_svc.create_profile.assert_called_once()
        call_args = self.resume_svc.create_profile.call_args
        assert call_args[0][0] == "user-123"  # user_id

    def test_create_profile_receives_resume_intelligence_create(self):
        from app.schemas import ResumeIntelligenceCreate

        self.service._stage_resume_intelligence(self.run, self.stage)

        call_args = self.resume_svc.create_profile.call_args
        schema = call_args[0][1]
        assert isinstance(schema, ResumeIntelligenceCreate)
        assert schema.raw_text == "John Doe, Python developer"

    def test_trigger_parse_called_with_correct_args(self):
        self.service._stage_resume_intelligence(self.run, self.stage)

        self.resume_svc.trigger_parse.assert_called_once_with(
            "profile-abc-123",  # profile_id
            "user-123",         # user_id
        )

    def test_run_resume_profile_id_populated(self):
        self.service._stage_resume_intelligence(self.run, self.stage)

        assert self.run.resume_profile_id == "profile-abc-123"

    def test_stage_entity_id_populated(self):
        self.service._stage_resume_intelligence(self.run, self.stage)

        assert self.stage.entity_id == "profile-abc-123"

    def test_create_profile_exception_propagates(self):
        self.resume_svc.create_profile.side_effect = Exception("DB error")

        with pytest.raises(Exception, match="DB error"):
            self.service._stage_resume_intelligence(self.run, self.stage)

    def test_trigger_parse_exception_propagates(self):
        self.resume_svc.trigger_parse.side_effect = Exception("Parse failed")

        with pytest.raises(Exception, match="Parse failed"):
            self.service._stage_resume_intelligence(self.run, self.stage)

    def test_create_profile_exception_before_trigger_parse(self):
        """If create_profile fails, trigger_parse should not be called."""
        self.resume_svc.create_profile.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            self.service._stage_resume_intelligence(self.run, self.stage)

        self.resume_svc.trigger_parse.assert_not_called()

    def test_stage_1_failure_causes_pipeline_failure(self):
        """Stage 1 is required — exception should cause pipeline failure."""
        self.resume_svc.create_profile.side_effect = Exception("Service unavailable")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_stage_1_success_allows_pipeline_continue(self):
        """Stage 1 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 1 should succeed — verify via the service's own mock
        self.service.resume_intelligence_service.create_profile.assert_called_once()


# ============================================================================
# TestStage2OpportunityIntelligence
# ============================================================================

class TestStage2OpportunityIntelligence:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-456")
        self.run.opportunity_text = "Senior Python Developer at Acme Corp"
        self.stage = _make_pipeline_stage(2)

        # Mock opportunity returned by create_opportunity
        self.mock_opportunity = MagicMock()
        self.mock_opportunity.id = "opp-abc-123"

        self.opp_svc = MagicMock()
        self.opp_svc.create_opportunity.return_value = self.mock_opportunity
        self.opp_svc.trigger_parse.return_value = self.mock_opportunity

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=self.opp_svc,
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_create_opportunity_called_with_correct_args(self):
        self.service._stage_opportunity(self.run, self.stage)

        self.opp_svc.create_opportunity.assert_called_once()
        call_args = self.opp_svc.create_opportunity.call_args
        assert call_args[0][0] == "user-456"  # user_id

    def test_create_opportunity_receives_opportunity_create(self):
        from app.schemas import OpportunityCreate

        self.service._stage_opportunity(self.run, self.stage)

        call_args = self.opp_svc.create_opportunity.call_args
        schema = call_args[0][1]
        assert isinstance(schema, OpportunityCreate)
        assert schema.raw_text == "Senior Python Developer at Acme Corp"

    def test_trigger_parse_called_with_correct_args(self):
        self.service._stage_opportunity(self.run, self.stage)

        self.opp_svc.trigger_parse.assert_called_once_with(
            "opp-abc-123",  # opportunity_id
            "user-456",      # user_id
        )

    def test_run_opportunity_id_populated(self):
        self.service._stage_opportunity(self.run, self.stage)

        assert self.run.opportunity_id == "opp-abc-123"

    def test_stage_entity_id_populated(self):
        self.service._stage_opportunity(self.run, self.stage)

        assert self.stage.entity_id == "opp-abc-123"

    def test_create_opportunity_exception_propagates(self):
        self.opp_svc.create_opportunity.side_effect = Exception("DB error")

        with pytest.raises(Exception, match="DB error"):
            self.service._stage_opportunity(self.run, self.stage)

    def test_trigger_parse_exception_propagates(self):
        self.opp_svc.trigger_parse.side_effect = Exception("Parse failed")

        with pytest.raises(Exception, match="Parse failed"):
            self.service._stage_opportunity(self.run, self.stage)

    def test_create_opportunity_exception_before_trigger_parse(self):
        """If create_opportunity fails, trigger_parse should not be called."""
        self.opp_svc.create_opportunity.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            self.service._stage_opportunity(self.run, self.stage)

        self.opp_svc.trigger_parse.assert_not_called()

    def test_stage_2_failure_causes_pipeline_failure(self):
        """Stage 2 is required — exception should cause pipeline failure."""
        self.opp_svc.create_opportunity.side_effect = Exception("Service unavailable")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_stage_2_success_allows_pipeline_continue(self):
        """Stage 2 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 2 should succeed — verify via the service's own mock
        self.service.opportunity_service.create_opportunity.assert_called_once()


# ============================================================================
# TestStage3GapAnalysis
# ============================================================================

class TestStage3GapAnalysis:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-789")
        self.run.resume_profile_id = "profile-123"
        self.run.opportunity_id = "opp-456"
        self.stage = _make_pipeline_stage(3)

        # Mock analysis returned by create
        self.mock_analysis = MagicMock()
        self.mock_analysis.id = "gap-abc-123"

        self.gap_svc = MagicMock()
        self.gap_svc.create.return_value = self.mock_analysis
        self.gap_svc.analyze.return_value = self.mock_analysis

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=self.gap_svc,
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_create_called_with_correct_args(self):
        self.service._stage_gap_analysis(self.run, self.stage)

        self.gap_svc.create.assert_called_once_with(
            "user-789",       # user_id
            "profile-123",    # resume_profile_id
            "opp-456",        # opportunity_id
        )

    def test_analyze_called_with_correct_args(self):
        self.service._stage_gap_analysis(self.run, self.stage)

        self.gap_svc.analyze.assert_called_once_with("gap-abc-123")

    def test_run_gap_analysis_id_populated(self):
        self.service._stage_gap_analysis(self.run, self.stage)

        assert self.run.gap_analysis_id == "gap-abc-123"

    def test_stage_entity_id_populated(self):
        self.service._stage_gap_analysis(self.run, self.stage)

        assert self.stage.entity_id == "gap-abc-123"

    def test_create_exception_propagates(self):
        self.gap_svc.create.side_effect = ValueError("Resume profile not found")

        with pytest.raises(ValueError, match="Resume profile not found"):
            self.service._stage_gap_analysis(self.run, self.stage)

    def test_analyze_exception_propagates(self):
        self.gap_svc.analyze.side_effect = ValueError("Analysis failed")

        with pytest.raises(ValueError, match="Analysis failed"):
            self.service._stage_gap_analysis(self.run, self.stage)

    def test_create_exception_before_analyze(self):
        """If create fails, analyze should not be called."""
        self.gap_svc.create.side_effect = ValueError("Duplicate")

        with pytest.raises(ValueError):
            self.service._stage_gap_analysis(self.run, self.stage)

        self.gap_svc.analyze.assert_not_called()

    def test_stage_3_failure_causes_pipeline_failure(self):
        """Stage 3 is required — exception should cause pipeline failure."""
        self.gap_svc.create.side_effect = ValueError("Resume profile not found")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_stage_3_success_allows_pipeline_continue(self):
        """Stage 3 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 3 should succeed — verify via the service's own mock
        self.service.gap_analysis_service.create.assert_called_once()


# ============================================================================
# TestStage4KnowledgeIntelligence
# ============================================================================

class TestStage4KnowledgeIntelligence:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-101")
        self.run.gap_analysis_id = "gap-789"
        self.stage = _make_pipeline_stage(4)

        # Mock retrieval returned by retrieve_knowledge
        self.mock_retrieval = MagicMock()
        self.mock_retrieval.id = "retr-abc-123"

        self.mock_context = MagicMock()
        self.mock_rules = [{"rule_id": "r1"}]

        self.knowledge_svc = MagicMock()
        self.knowledge_svc.retrieve_knowledge.return_value = {
            "retrieval": self.mock_retrieval,
            "context": self.mock_context,
            "rules": self.mock_rules,
        }

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=self.knowledge_svc,
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_retrieve_knowledge_called_with_correct_args(self):
        self.service._stage_knowledge(self.run, self.stage)

        self.knowledge_svc.retrieve_knowledge.assert_called_once_with(
            "gap-789",  # gap_analysis_id
            "user-101",  # user_id
        )

    def test_run_knowledge_retrieval_id_populated(self):
        self.service._stage_knowledge(self.run, self.stage)

        assert self.run.knowledge_retrieval_id == "retr-abc-123"

    def test_stage_entity_id_populated(self):
        self.service._stage_knowledge(self.run, self.stage)

        assert self.stage.entity_id == "retr-abc-123"

    def test_retrieve_knowledge_exception_does_not_fail_pipeline(self):
        """Stage 4 is non-fatal — exception should not propagate via _execute_stage."""
        self.knowledge_svc.retrieve_knowledge.side_effect = ValueError("Gap analysis not found")

        # Non-fatal handling is in _execute_stage, not _stage_knowledge
        result = self.service._execute_stage(
            self.run, self.stage, self.service._stage_knowledge
        )

        # Should NOT raise — stage marked failed but result returned
        assert result.status == "failed"
        assert result.error == "Gap analysis not found"

    def test_stage_4_failure_marks_stage_failed(self):
        """Stage 4 failure should mark stage as failed via _execute_stage."""
        self.knowledge_svc.retrieve_knowledge.side_effect = ValueError("Service error")

        result = self.service._execute_stage(
            self.run, self.stage, self.service._stage_knowledge
        )

        assert result.status == "failed"
        assert result.error == "Service error"

    def test_stage_4_failure_allows_pipeline_continue(self):
        """Stage 4 failure should not block pipeline."""
        self.knowledge_svc.retrieve_knowledge.side_effect = ValueError("Service error")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        # Configure create_batch to return proper stages with stage_order
        self.service.pipeline_stage_repo.create_batch.return_value = [
            _make_pipeline_stage(i + 1) for i in range(7)
        ]

        result = self.service.execute_pipeline(request, "user-1")

        # Pipeline should complete despite Stage 4 failure
        assert result.status == "completed"

    def test_stage_4_success_allows_pipeline_continue(self):
        """Stage 4 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 4 should succeed — verify via the service's own mock
        self.service.knowledge_intelligence_service.retrieve_knowledge.assert_called_once()


# ============================================================================
# TestStage5PromptIntelligence
# ============================================================================

class TestStage5PromptIntelligence:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-202")
        self.run.gap_analysis_id = "gap-456"
        self.stage = _make_pipeline_stage(5)

        # Mock package returned by build_prompt
        self.mock_package = MagicMock()
        self.mock_package.id = "pkg-xyz-789"

        self.prompt_svc = MagicMock()
        self.prompt_svc.build_prompt.return_value = {
            "package": self.mock_package,
            "validation": {"is_valid": True, "errors": []},
            "tokens_estimate": 200,
        }

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=self.prompt_svc,
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_build_prompt_called_with_correct_args(self):
        self.service._stage_prompt(self.run, self.stage)

        self.prompt_svc.build_prompt.assert_called_once_with(
            "user-202",  # user_id
            "gap-456",    # gap_analysis_id
        )

    def test_run_prompt_package_id_populated(self):
        self.service._stage_prompt(self.run, self.stage)

        assert self.run.prompt_package_id == "pkg-xyz-789"

    def test_stage_entity_id_populated(self):
        self.service._stage_prompt(self.run, self.stage)

        assert self.stage.entity_id == "pkg-xyz-789"

    def test_build_prompt_exception_propagates(self):
        self.prompt_svc.build_prompt.side_effect = ValueError("Gap analysis not found")

        with pytest.raises(ValueError, match="Gap analysis not found"):
            self.service._stage_prompt(self.run, self.stage)

    def test_stage_5_failure_causes_pipeline_failure(self):
        """Stage 5 is required — exception should cause pipeline failure."""
        self.prompt_svc.build_prompt.side_effect = ValueError("Service unavailable")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_stage_5_success_allows_pipeline_continue(self):
        """Stage 5 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 5 should succeed — verify via the service's own mock
        self.service.prompt_intelligence_service.build_prompt.assert_called_once()


# ============================================================================
# TestStage6AIExecution
# ============================================================================

class TestStage6AIExecution:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-303")
        self.run.prompt_package_id = "pkg-789"
        self.stage = _make_pipeline_stage(6)
        self.stage.metadata_ = {}

        # Mock result returned by execute_prompt_package
        self.mock_result = {
            "execution_id": "exec-abc-456",
            "status": "completed",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "parsed_response": {"summary": "Generated resume"},
        }

        self.execution_svc = MagicMock()
        self.execution_svc.execute_prompt_package.return_value = self.mock_result

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=self.execution_svc,
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_execute_prompt_package_called_with_correct_args(self):
        self.service._stage_execution(self.run, self.stage)

        self.execution_svc.execute_prompt_package.assert_called_once_with(
            "user-303",  # user_id
            "pkg-789",    # prompt_package_id
        )

    def test_run_ai_execution_id_populated(self):
        self.service._stage_execution(self.run, self.stage)

        assert self.run.ai_execution_id == "exec-abc-456"

    def test_stage_entity_id_populated(self):
        self.service._stage_execution(self.run, self.stage)

        assert self.stage.entity_id == "exec-abc-456"

    def test_stage_metadata_stores_parsed_response(self):
        self.service._stage_execution(self.run, self.stage)

        assert self.stage.metadata_["parsed_response"] == {"summary": "Generated resume"}

    def test_execute_prompt_package_exception_propagates(self):
        from app.services.ai_service import ProviderError

        self.execution_svc.execute_prompt_package.side_effect = ProviderError("Provider failed")

        with pytest.raises(ProviderError, match="Provider failed"):
            self.service._stage_execution(self.run, self.stage)

    def test_stage_6_failure_causes_pipeline_failure(self):
        """Stage 6 is required — exception should cause pipeline failure."""
        from app.services.ai_service import ProviderError

        self.execution_svc.execute_prompt_package.side_effect = ProviderError("Service unavailable")

        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.error is not None

    def test_stage_6_success_allows_pipeline_continue(self):
        """Stage 6 success should not block pipeline."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 6 should succeed — verify via the service's own mock
        self.service.ai_execution_service.execute_prompt_package.assert_called_once()


# ============================================================================
# TestStage7AIResponseIntelligence
# ============================================================================

class TestStage7AIResponseIntelligence:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run(user_id="user-404")
        self.run.ai_execution_id = "exec-789"
        self.stage = _make_pipeline_stage(7)
        self.stage.metadata_ = {}

        # Mock result returned by validate_ai_response
        self.mock_result = {
            "validation_id": "val-abc-101",
            "status": "completed",
            "validation_result": {"confidence": 85, "status": "approved"},
        }

        self.validation_svc = MagicMock()
        self.validation_svc.validate_ai_response.return_value = self.mock_result

        self.stage_repo = MagicMock(spec=PipelineStageRepository)

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=self.validation_svc,
            pipeline_run_repo=MagicMock(),
            pipeline_stage_repo=self.stage_repo,
        )

        # Configure mocks for execute_pipeline integration test
        self.service.pipeline_run_repo.create.return_value = self.run
        self.service.pipeline_stage_repo.create.return_value = self.stage

    def test_validate_ai_response_called_with_correct_args(self):
        self.service._stage_validation(self.run, self.stage)

        self.validation_svc.validate_ai_response.assert_called_once_with(
            "user-404",  # user_id
            "exec-789",   # ai_execution_id
        )

    def test_run_ai_validation_id_populated(self):
        self.service._stage_validation(self.run, self.stage)

        assert self.run.ai_validation_id == "val-abc-101"

    def test_stage_entity_id_populated(self):
        self.service._stage_validation(self.run, self.stage)

        assert self.stage.entity_id == "val-abc-101"

    def test_stage_metadata_stores_validation_result(self):
        self.service._stage_validation(self.run, self.stage)

        assert self.stage.metadata_["validation_result"] == {"confidence": 85, "status": "approved"}

    def test_validate_ai_response_exception_propagates(self):
        self.validation_svc.validate_ai_response.side_effect = ValueError("Execution not found")

        with pytest.raises(ValueError, match="Execution not found"):
            self.service._stage_validation(self.run, self.stage)

    def test_stage_7_failure_does_not_fail_pipeline(self):
        """Stage 7 is non-fatal — exception should not propagate via _execute_stage."""
        self.validation_svc.validate_ai_response.side_effect = ValueError("Validation service error")

        result = self.service._execute_stage(
            self.run, self.stage, self.service._stage_validation
        )

        # Should NOT raise — stage marked failed but result returned
        assert result.status == "failed"
        assert result.error == "Validation service error"

    def test_stage_7_success_allows_pipeline_completion(self):
        """Stage 7 success should allow pipeline to complete."""
        request = PipelineRequest(
            resume_text="resume",
            opportunity_text="job",
        )

        # Mock all other stage functions to succeed
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
        ]:
            setattr(self.service, attr, MagicMock())

        result = self.service.execute_pipeline(request, "user-1")

        # Stage 7 should succeed — verify via the service's own mock
        self.service.ai_response_intelligence_service.validate_ai_response.assert_called_once()


# ============================================================================
# TestExecutePipelineOrchestration — Comprehensive Task 2.8 Tests
# ============================================================================

class TestExecutePipelineOrchestration:
    def setup_method(self):
        self.db = MagicMock()
        self.run = _make_pipeline_run()
        self.stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        for s in self.stages:
            s.metadata_ = {}

        self.run_repo = MagicMock(spec=PipelineRunRepository)
        self.run_repo.create.return_value = self.run

        self.stage_repo = MagicMock(spec=PipelineStageRepository)
        self.stage_repo.create_batch.return_value = self.stages

        self.service = IntelligencePipelineService(
            db=self.db,
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def _mock_all_stages_succeed(self):
        for attr in [
            "_stage_resume_intelligence",
            "_stage_opportunity",
            "_stage_gap_analysis",
            "_stage_knowledge",
            "_stage_prompt",
            "_stage_execution",
            "_stage_validation",
        ]:
            setattr(self.service, attr, MagicMock())

    def test_full_happy_path_all_stages_complete(self):
        """All 7 stages execute in order, pipeline completes."""
        self._mock_all_stages_succeed()
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "completed"
        assert len(result.stages) == 7
        for sr in result.stages:
            assert sr.status == "completed"

    def test_stage_1_failure_stops_pipeline(self):
        """Stage 1 failure prevents stages 2-7 from executing."""
        self.service._stage_resume_intelligence = MagicMock(
            side_effect=ValueError("Stage 1 failed")
        )
        self._mock_all_stages_succeed()
        # Override stage 1 to fail
        self.service._stage_resume_intelligence = MagicMock(
            side_effect=ValueError("Stage 1 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.stages[0].status == "failed"
        # Stages 2-7 should remain pending (never executed)
        for sr in result.stages[1:]:
            assert sr.status == "pending"

    def test_stage_2_failure_stops_pipeline(self):
        """Stage 2 failure prevents stages 3-7 from executing."""
        self._mock_all_stages_succeed()
        self.service._stage_opportunity = MagicMock(
            side_effect=ValueError("Stage 2 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.stages[0].status == "completed"
        assert result.stages[1].status == "failed"
        for sr in result.stages[2:]:
            assert sr.status == "pending"

    def test_stage_3_failure_stops_pipeline(self):
        """Stage 3 failure prevents stages 4-7 from executing."""
        self._mock_all_stages_succeed()
        self.service._stage_gap_analysis = MagicMock(
            side_effect=ValueError("Stage 3 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.stages[0].status == "completed"
        assert result.stages[1].status == "completed"
        assert result.stages[2].status == "failed"
        for sr in result.stages[3:]:
            assert sr.status == "pending"

    def test_stage_4_failure_allows_pipeline_continue(self):
        """Stage 4 (non-fatal) failure allows stages 5-7 to execute."""
        self._mock_all_stages_succeed()
        self.service._stage_knowledge = MagicMock(
            side_effect=ValueError("Stage 4 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "completed"
        assert result.stages[3].status == "failed"
        assert result.stages[4].status == "completed"
        assert result.stages[5].status == "completed"
        assert result.stages[6].status == "completed"

    def test_stage_5_failure_stops_pipeline(self):
        """Stage 5 failure prevents stages 6-7 from executing."""
        self._mock_all_stages_succeed()
        self.service._stage_prompt = MagicMock(
            side_effect=ValueError("Stage 5 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.stages[3].status == "completed"
        assert result.stages[4].status == "failed"
        for sr in result.stages[5:]:
            assert sr.status == "pending"

    def test_stage_6_failure_stops_pipeline(self):
        """Stage 6 failure prevents stage 7 from executing."""
        self._mock_all_stages_succeed()
        self.service._stage_execution = MagicMock(
            side_effect=ValueError("Stage 6 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert result.stages[5].status == "failed"
        assert result.stages[6].status == "pending"

    def test_stage_7_failure_does_not_fail_pipeline(self):
        """Stage 7 (non-fatal) failure does not fail the pipeline."""
        self._mock_all_stages_succeed()
        self.service._stage_validation = MagicMock(
            side_effect=ValueError("Stage 7 failed")
        )
        request = PipelineRequest(resume_text="resume", opportunity_text="job")

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "completed"
        assert result.stages[6].status == "failed"

    def test_skip_validation_skips_stage_7(self):
        """skip_validation=True skips Stage 7."""
        self._mock_all_stages_succeed()
        request = PipelineRequest(
            resume_text="resume", opportunity_text="job", skip_validation=True
        )

        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "completed"
        self.service._stage_validation.assert_not_called()
        assert self.stages[6].status == "skipped"

    def test_entity_id_propagation_all_seven(self):
        """PipelineResult contains IDs populated by all 7 stages."""
        self._mock_all_stages_succeed()

        # Set entity IDs on mock stages after execution
        def set_ids(run, stage):
            if stage.stage_order == 1:
                run.resume_profile_id = "rp-1"
                stage.entity_id = "rp-1"
            elif stage.stage_order == 2:
                run.opportunity_id = "opp-1"
                stage.entity_id = "opp-1"
            elif stage.stage_order == 3:
                run.gap_analysis_id = "ga-1"
                stage.entity_id = "ga-1"
            elif stage.stage_order == 4:
                run.knowledge_retrieval_id = "kr-1"
                stage.entity_id = "kr-1"
            elif stage.stage_order == 5:
                run.prompt_package_id = "pp-1"
                stage.entity_id = "pp-1"
            elif stage.stage_order == 6:
                run.ai_execution_id = "ae-1"
                stage.entity_id = "ae-1"
            elif stage.stage_order == 7:
                run.ai_validation_id = "av-1"
                stage.entity_id = "av-1"

        self.service._stage_resume_intelligence = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_opportunity = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_gap_analysis = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_knowledge = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_prompt = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_execution = MagicMock(side_effect=lambda r, s: set_ids(r, s))
        self.service._stage_validation = MagicMock(side_effect=lambda r, s: set_ids(r, s))

        request = PipelineRequest(resume_text="resume", opportunity_text="job")
        result = self.service.execute_pipeline(request, "user-1")

        assert result.resume_profile_id == "rp-1"
        assert result.opportunity_id == "opp-1"
        assert result.gap_analysis_id == "ga-1"
        assert result.knowledge_retrieval_id == "kr-1"
        assert result.prompt_package_id == "pp-1"
        assert result.ai_execution_id == "ae-1"
        assert result.ai_validation_id == "av-1"


# --- Tasks 3.2 & 3.3: Boundary Tests ---

class TestUniversalAIBoundary:
    """Task 3.2: Verify pipeline does NOT import Universal AI Engine."""

    def test_no_universal_ai_service_import(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        assert "app.services.universal_ai" not in imports
        assert "app.services.ai_execution" not in imports

    def test_no_provider_sdk_import(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        for provider in ["openai", "anthropic", "google.generativeai"]:
            assert provider not in imports

    def test_no_generate_call(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "generate":
                    assert False, "Pipeline calls generate() directly"
                elif isinstance(func, ast.Name) and func.id == "generate":
                    assert False, "Pipeline calls generate() directly"


class TestPromptIntelligenceBoundary:
    """Task 3.3: Verify pipeline does NOT import Prompt Intelligence internals."""

    def test_no_prompt_builder_import(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        assert "app.services.prompt_intelligence.v2_builder" not in imports
        assert "app.services.prompt_intelligence.builder" not in imports

    def test_no_prompt_request_import(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "prompt_intelligence" in node.module:
                    for alias in node.names:
                        assert alias.name != "PromptRequest", (
                            "Pipeline imports PromptRequest from prompt_intelligence"
                        )

    def test_no_direct_prompt_construction(self):
        import ast
        with open("app/services/intelligence_pipeline/service.py") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    name = func.id
                    if name in ("PromptBuilderV2", "PromptBuilder", "PromptRequest"):
                        assert False, f"Pipeline constructs prompts via {name}()"


# --- Task 4.1: Pipeline Status Retrieval ---

class TestGetPipelineStatus:
    """Task 4.1: get_pipeline_status retrieval and error handling."""

    def setup_method(self):
        self.run_repo = MagicMock()
        self.stage_repo = MagicMock()
        self.service = IntelligencePipelineService(
            db=MagicMock(),
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_happy_path_returns_pipeline_result(self):
        run = _make_pipeline_run(id="run-1")
        run.status = "completed"
        run.total_latency_ms = 1234.5
        run.error_message = None
        run.resume_profile_id = "rp-1"
        run.opportunity_id = "opp-1"
        run.gap_analysis_id = "ga-1"
        run.knowledge_retrieval_id = "kr-1"
        run.prompt_package_id = "pp-1"
        run.ai_execution_id = "ae-1"
        run.ai_validation_id = "av-1"
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        for s in stages:
            s.status = "completed"
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-1")

        assert isinstance(result, PipelineResult)
        assert result.pipeline_run_id == "run-1"
        assert result.status == "completed"
        assert result.resume_profile_id == "rp-1"
        assert result.opportunity_id == "opp-1"
        assert result.gap_analysis_id == "ga-1"
        assert result.knowledge_retrieval_id == "kr-1"
        assert result.prompt_package_id == "pp-1"
        assert result.ai_execution_id == "ae-1"
        assert result.ai_validation_id == "av-1"
        assert result.total_latency_ms == 1234.5

    def test_happy_path_calls_repos_with_correct_id(self):
        self.run_repo.get_by_id.return_value = None

        self.service.get_pipeline_status("run-42")

        self.run_repo.get_by_id.assert_called_once_with("run-42")

    def test_missing_run_returns_error_result(self):
        self.run_repo.get_by_id.return_value = None

        result = self.service.get_pipeline_status("nonexistent")

        assert isinstance(result, PipelineResult)
        assert result.pipeline_run_id == "nonexistent"
        assert result.status == "failed"
        assert result.stages == []
        assert "not found" in result.error.lower()

    def test_missing_run_does_not_call_stage_repo(self):
        self.run_repo.get_by_id.return_value = None

        self.service.get_pipeline_status("nonexistent")

        self.stage_repo.get_by_run_id.assert_not_called()

    def test_stage_mapping_preserves_all_seven_stages(self):
        run = _make_pipeline_run(id="run-2")
        run.status = "completed"
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-2")

        assert len(result.stages) == 7
        for i, stage_result in enumerate(result.stages):
            assert stage_result.stage_order == i + 1
            assert stage_result.stage_name == STAGE_NAMES[i]

    def test_stage_mapping_preserves_status(self):
        run = _make_pipeline_run(id="run-3")
        run.status = "failed"
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[0].status = "completed"
        stages[1].status = "completed"
        stages[2].status = "failed"
        stages[2].error_message = "Missing resume_profile_id"
        for i in range(3, 7):
            stages[i].status = "pending"
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-3")

        assert result.stages[0].status == "completed"
        assert result.stages[1].status == "completed"
        assert result.stages[2].status == "failed"
        assert result.stages[2].error == "Missing resume_profile_id"
        for i in range(3, 7):
            assert result.stages[i].status == "pending"

    def test_stage_mapping_preserves_entity_ids(self):
        run = _make_pipeline_run(id="run-4")
        run.status = "completed"
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[0].entity_id = "rp-1"
        stages[1].entity_id = "opp-1"
        stages[2].entity_id = "ga-1"
        stages[3].entity_id = "kr-1"
        stages[4].entity_id = "pp-1"
        stages[5].entity_id = "ae-1"
        stages[6].entity_id = "av-1"
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-4")

        assert result.stages[0].entity_id == "rp-1"
        assert result.stages[1].entity_id == "opp-1"
        assert result.stages[2].entity_id == "ga-1"
        assert result.stages[3].entity_id == "kr-1"
        assert result.stages[4].entity_id == "pp-1"
        assert result.stages[5].entity_id == "ae-1"
        assert result.stages[6].entity_id == "av-1"

    def test_stage_mapping_preserves_latency_and_metadata(self):
        run = _make_pipeline_run(id="run-5")
        run.status = "completed"
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[0].latency_ms = 1200.5
        stages[0].metadata_ = {"key": "value"}
        stages[1].latency_ms = 800.0
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-5")

        assert result.stages[0].latency_ms == 1200.5
        assert result.stages[0].metadata == {"key": "value"}
        assert result.stages[1].latency_ms == 800.0

    def test_failed_pipeline_returns_persisted_status(self):
        run = _make_pipeline_run(id="run-6")
        run.status = "failed"
        run.error_message = "Pipeline failed at stage 3: gap_analysis"
        run.total_latency_ms = 2150.0
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[0].status = "completed"
        stages[1].status = "completed"
        stages[2].status = "failed"
        stages[2].error_message = "Missing required field: resume_profile_id"
        for i in range(3, 7):
            stages[i].status = "pending"
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-6")

        assert result.status == "failed"
        assert result.error == "Pipeline failed at stage 3: gap_analysis"
        assert result.total_latency_ms == 2150.0

    def test_running_pipeline_returns_pending_stages(self):
        run = _make_pipeline_run(id="run-7")
        run.status = "running"
        run.total_latency_ms = 0.0
        self.run_repo.get_by_id.return_value = run

        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[0].status = "completed"
        stages[1].status = "running"
        for i in range(2, 7):
            stages[i].status = "pending"
        self.stage_repo.get_by_run_id.return_value = stages

        result = self.service.get_pipeline_status("run-7")

        assert result.status == "running"
        assert result.stages[0].status == "completed"
        assert result.stages[1].status == "running"
        for i in range(2, 7):
            assert result.stages[i].status == "pending"

    def test_read_only_does_not_modify_database(self):
        run = _make_pipeline_run(id="run-8")
        self.run_repo.get_by_id.return_value = run
        self.stage_repo.get_by_run_id.return_value = []

        self.service.get_pipeline_status("run-8")

        self.run_repo.update_status.assert_not_called()
        self.run_repo.update_entity_ids.assert_not_called()
        self.stage_repo.update_status.assert_not_called()


# --- Task 4.2: Pipeline Run Listing ---

class TestListPipelineRuns:
    """Task 4.2: list_pipeline_runs retrieval and pagination."""

    def setup_method(self):
        self.run_repo = MagicMock()
        self.stage_repo = MagicMock()
        self.service = IntelligencePipelineService(
            db=MagicMock(),
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_happy_path_returns_list_of_pipeline_results(self):
        run1 = _make_pipeline_run(id="run-1", user_id="user-1")
        run1.status = "completed"
        run2 = _make_pipeline_run(id="run-2", user_id="user-1")
        run2.status = "failed"
        self.run_repo.get_by_user_id.return_value = ([run1, run2], 2)

        self.stage_repo.get_by_run_id.return_value = []

        results = self.service.list_pipeline_runs("user-1")

        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0].pipeline_run_id == "run-1"
        assert results[0].status == "completed"
        assert results[1].pipeline_run_id == "run-2"
        assert results[1].status == "failed"

    def test_happy_path_calls_repo_with_correct_args(self):
        self.run_repo.get_by_user_id.return_value = ([], 0)

        self.service.list_pipeline_runs("user-42", skip=10, limit=5)

        self.run_repo.get_by_user_id.assert_called_once_with(
            "user-42", skip=10, limit=5
        )

    def test_empty_results_returns_empty_list(self):
        self.run_repo.get_by_user_id.return_value = ([], 0)

        results = self.service.list_pipeline_runs("user-no-runs")

        assert results == []

    def test_stage_mapping_includes_stages_for_each_run(self):
        run1 = _make_pipeline_run(id="run-1", user_id="user-1")
        run1.status = "completed"
        run2 = _make_pipeline_run(id="run-2", user_id="user-1")
        run2.status = "completed"
        self.run_repo.get_by_user_id.return_value = ([run1, run2], 2)

        stages_run1 = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages_run2 = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages_run2[0].entity_id = "rp-99"
        self.stage_repo.get_by_run_id.side_effect = [stages_run1, stages_run2]

        results = self.service.list_pipeline_runs("user-1")

        assert len(results[0].stages) == 7
        assert len(results[1].stages) == 7
        assert results[1].stages[0].entity_id == "rp-99"

    def test_preserves_entity_ids_from_persisted_run(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        run.status = "completed"
        run.resume_profile_id = "rp-1"
        run.opportunity_id = "opp-1"
        run.gap_analysis_id = "ga-1"
        run.knowledge_retrieval_id = "kr-1"
        run.prompt_package_id = "pp-1"
        run.ai_execution_id = "ae-1"
        run.ai_validation_id = "av-1"
        self.run_repo.get_by_user_id.return_value = ([run], 1)
        self.stage_repo.get_by_run_id.return_value = []

        results = self.service.list_pipeline_runs("user-1")

        assert results[0].resume_profile_id == "rp-1"
        assert results[0].opportunity_id == "opp-1"
        assert results[0].gap_analysis_id == "ga-1"
        assert results[0].knowledge_retrieval_id == "kr-1"
        assert results[0].prompt_package_id == "pp-1"
        assert results[0].ai_execution_id == "ae-1"
        assert results[0].ai_validation_id == "av-1"

    def test_preserves_ordering_from_repository(self):
        run1 = _make_pipeline_run(id="run-old", user_id="user-1")
        run1.status = "completed"
        run2 = _make_pipeline_run(id="run-new", user_id="user-1")
        run2.status = "completed"
        self.run_repo.get_by_user_id.return_value = ([run1, run2], 2)
        self.stage_repo.get_by_run_id.return_value = []

        results = self.service.list_pipeline_runs("user-1")

        assert results[0].pipeline_run_id == "run-old"
        assert results[1].pipeline_run_id == "run-new"

    def test_user_filtering_passes_user_id_to_repo(self):
        self.run_repo.get_by_user_id.return_value = ([], 0)

        self.service.list_pipeline_runs("user-A")
        self.run_repo.get_by_user_id.assert_called_with("user-A", skip=0, limit=20)

        self.service.list_pipeline_runs("user-B", skip=5, limit=10)
        self.run_repo.get_by_user_id.assert_called_with("user-B", skip=5, limit=10)

    def test_read_only_does_not_modify_database(self):
        self.run_repo.get_by_user_id.return_value = ([], 0)

        self.service.list_pipeline_runs("user-1")

        self.run_repo.update_status.assert_not_called()
        self.run_repo.update_entity_ids.assert_not_called()
        self.run_repo.create.assert_not_called()
        self.stage_repo.update_status.assert_not_called()
        self.stage_repo.create_batch.assert_not_called()

    def test_preserves_latency_and_error_from_run(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        run.status = "failed"
        run.error_message = "Pipeline failed at stage 3: gap_analysis"
        run.total_latency_ms = 2150.0
        self.run_repo.get_by_user_id.return_value = ([run], 1)
        self.stage_repo.get_by_run_id.return_value = []

        results = self.service.list_pipeline_runs("user-1")

        assert results[0].error == "Pipeline failed at stage 3: gap_analysis"
        assert results[0].total_latency_ms == 2150.0

    def test_default_pagination_values(self):
        self.run_repo.get_by_user_id.return_value = ([], 0)

        self.service.list_pipeline_runs("user-1")

        self.run_repo.get_by_user_id.assert_called_once_with(
            "user-1", skip=0, limit=20
        )


# --- Task 4.3: Error Information Capture ---

class TestErrorInformationCapture:
    """Task 4.3: Error message capture and metadata population."""

    def setup_method(self):
        self.run_repo = MagicMock()
        self.stage_repo = MagicMock()
        self.service = IntelligencePipelineService(
            db=MagicMock(),
            resume_intelligence_service=MagicMock(),
            opportunity_service=MagicMock(),
            gap_analysis_service=MagicMock(),
            knowledge_intelligence_service=MagicMock(),
            prompt_intelligence_service=MagicMock(),
            ai_execution_service=MagicMock(),
            ai_response_intelligence_service=MagicMock(),
            pipeline_run_repo=self.run_repo,
            pipeline_stage_repo=self.stage_repo,
        )

    def test_stage_metadata_populated_on_failure(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stage = _make_pipeline_stage(4)
        stage.metadata_ = {}

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ValueError("missing field")

        self.service._execute_stage(run, stage, self.service._stage_knowledge)

        assert "error" in stage.metadata_
        assert stage.metadata_["error"]["exception_type"] == "ValueError"
        assert stage.metadata_["error"]["stage"] == "knowledge_intelligence"
        assert stage.metadata_["error"]["message"] == "missing field"

    def test_stage_metadata_preserves_existing_metadata(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stage = _make_pipeline_stage(4)
        stage.metadata_ = {"existing_key": "existing_value"}

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ValueError("error")

        self.service._execute_stage(run, stage, self.service._stage_knowledge)

        assert stage.metadata_["existing_key"] == "existing_value"
        assert "error" in stage.metadata_

    def test_stage_metadata_handles_none_metadata(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stage = _make_pipeline_stage(4)
        stage.metadata_ = None

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ValueError("error")

        self.service._execute_stage(run, stage, self.service._stage_knowledge)

        assert stage.metadata_ is not None
        assert "error" in stage.metadata_

    def test_pipeline_run_error_includes_stage_name(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        self.stage_repo.create_batch.return_value = stages
        self.run_repo.create.return_value = run

        self.service.resume_intelligence_service.create_profile.side_effect = ValueError("missing field")

        request = PipelineRequest(resume_text="resume", opportunity_text="job")
        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "failed"
        assert "resume_intelligence" in result.error
        assert "missing field" in result.error
        assert result.error == "Stage resume_intelligence failed: missing field"

    def test_pipeline_run_error_format_exact(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        stages[4].stage_name = "prompt_intelligence"
        self.stage_repo.create_batch.return_value = stages
        self.run_repo.create.return_value = run

        self.service.prompt_intelligence_service.build_prompt.side_effect = RuntimeError("API timeout")

        request = PipelineRequest(resume_text="resume", opportunity_text="job")
        result = self.service.execute_pipeline(request, "user-1")

        assert result.error == "Stage prompt_intelligence failed: API timeout"

    def test_traceback_not_stored_in_metadata(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stage = _make_pipeline_stage(4)

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ValueError("error")

        self.service._execute_stage(run, stage, self.service._stage_knowledge)

        metadata_str = str(stage.metadata_)
        assert "traceback" not in metadata_str.lower()
        assert "Traceback" not in metadata_str

    def test_non_fatal_stage_metadata_populated(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stage = _make_pipeline_stage(4)
        stage.metadata_ = {}

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ConnectionError("timeout")

        self.service._execute_stage(run, stage, self.service._stage_knowledge)

        assert "error" in stage.metadata_
        assert stage.metadata_["error"]["exception_type"] == "ConnectionError"
        assert stage.metadata_["error"]["stage"] == "knowledge_intelligence"
        assert stage.metadata_["error"]["message"] == "timeout"

    def test_non_fatal_stage_failure_does_not_set_pipeline_error(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        self.stage_repo.create_batch.return_value = stages
        self.run_repo.create.return_value = run

        self.service.knowledge_intelligence_service.retrieve_knowledge.side_effect = ConnectionError("timeout")
        self.service.prompt_intelligence_service.build_prompt.return_value = {"package": MagicMock(id="pp-1")}
        self.service.ai_execution_service.execute_prompt_package.return_value = {"execution_id": "ae-1", "parsed_response": None}

        request = PipelineRequest(resume_text="resume", opportunity_text="job")
        result = self.service.execute_pipeline(request, "user-1")

        assert result.status == "completed"
        assert result.error is None

    def test_required_stage_failure_captures_error_in_pipeline_run(self):
        run = _make_pipeline_run(id="run-1", user_id="user-1")
        stages = [_make_pipeline_stage(i + 1) for i in range(7)]
        self.stage_repo.create_batch.return_value = stages
        self.run_repo.create.return_value = run

        self.service.resume_intelligence_service.create_profile.side_effect = ValueError("bad input")

        request = PipelineRequest(resume_text="resume", opportunity_text="job")
        result = self.service.execute_pipeline(request, "user-1")

        self.run_repo.update_status.assert_called()
        call_args = self.run_repo.update_status.call_args
        assert call_args[0][0] == "run-1"
        assert call_args[0][1] == "failed"
        assert call_args[1]["error_message"] == "Stage resume_intelligence failed: bad input"
