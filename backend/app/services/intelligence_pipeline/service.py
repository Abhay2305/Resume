"""Intelligence Pipeline Service.

Thin orchestration layer connecting 7 intelligence services into a single
executable pipeline. Composes existing services; does not modify them.
"""
import logging
import time
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.models.pipeline import PipelineRun, PipelineStage
from app.repositories.pipeline import PipelineRunRepository, PipelineStageRepository
from app.schemas import OpportunityCreate, ResumeIntelligenceCreate
from app.services.intelligence_pipeline.types import (
    PipelineRequest,
    PipelineResult,
    StageResult,
)

logger = logging.getLogger(__name__)

# Stage names in execution order
STAGE_NAMES = [
    "resume_intelligence",       # Stage 1
    "opportunity_intelligence",  # Stage 2
    "gap_analysis",              # Stage 3
    "knowledge_intelligence",    # Stage 4 (non-fatal)
    "prompt_intelligence",       # Stage 5
    "ai_execution",              # Stage 6
    "ai_response_intelligence",  # Stage 7 (non-fatal, skippable)
]

# Stages that cause pipeline failure if they fail
REQUIRED_STAGES = {1, 2, 3, 5, 6}

# Stages that are non-fatal (pipeline continues on failure)
NON_FATAL_STAGES = {4, 7}


class IntelligencePipelineService:
    """Orchestrates the 7-stage intelligence pipeline.

    All service dependencies are injected via constructor. No services
    are instantiated internally. This service composes existing services;
    it does not modify them.
    """

    def __init__(
        self,
        db,
        resume_intelligence_service,
        opportunity_service,
        gap_analysis_service,
        knowledge_intelligence_service,
        prompt_intelligence_service,
        ai_execution_service,
        ai_response_intelligence_service,
        pipeline_run_repo: PipelineRunRepository,
        pipeline_stage_repo: PipelineStageRepository,
    ):
        self.db = db
        self.resume_intelligence_service = resume_intelligence_service
        self.opportunity_service = opportunity_service
        self.gap_analysis_service = gap_analysis_service
        self.knowledge_intelligence_service = knowledge_intelligence_service
        self.prompt_intelligence_service = prompt_intelligence_service
        self.ai_execution_service = ai_execution_service
        self.ai_response_intelligence_service = ai_response_intelligence_service
        self.pipeline_run_repo = pipeline_run_repo
        self.pipeline_stage_repo = pipeline_stage_repo

    def execute_pipeline(
        self, request: PipelineRequest, user_id: str
    ) -> PipelineResult:
        """Execute the full 7-stage intelligence pipeline.

        Creates PipelineRun + PipelineStage records, then executes stages
        sequentially. Returns PipelineResult with all entity IDs.
        """
        pipeline_start = time.time()

        # 1. Create PipelineRun record
        run = self.pipeline_run_repo.create({
            "user_id": user_id,
            "status": "running",
            "resume_text": request.resume_text,
            "opportunity_text": request.opportunity_text,
        })

        # 2. Create all 7 stage records (pending)
        stage_data = [
            {
                "pipeline_run_id": run.id,
                "stage_name": name,
                "stage_order": i + 1,
                "status": "pending",
            }
            for i, name in enumerate(STAGE_NAMES)
        ]
        stages = self.pipeline_stage_repo.create_batch(stage_data)

        try:
            # Stage 1: Resume Intelligence (required)
            current_stage_name = stages[0].stage_name
            result = self._execute_stage(run, stages[0], self._stage_resume_intelligence)
            if result.failed:
                return self._build_result(run, stages, "failed", pipeline_start)

            # Stage 2: Opportunity Intelligence (required)
            current_stage_name = stages[1].stage_name
            result = self._execute_stage(run, stages[1], self._stage_opportunity)
            if result.failed:
                return self._build_result(run, stages, "failed", pipeline_start)

            # Stage 3: Gap Analysis (required)
            current_stage_name = stages[2].stage_name
            result = self._execute_stage(run, stages[2], self._stage_gap_analysis)
            if result.failed:
                return self._build_result(run, stages, "failed", pipeline_start)

            # Stage 4: Knowledge Intelligence (non-fatal)
            current_stage_name = stages[3].stage_name
            result = self._execute_stage(run, stages[3], self._stage_knowledge)
            # Knowledge failure is non-fatal: pipeline continues with empty context

            # Stage 5: Prompt Intelligence (required)
            current_stage_name = stages[4].stage_name
            result = self._execute_stage(run, stages[4], self._stage_prompt)
            if result.failed:
                return self._build_result(run, stages, "failed", pipeline_start)

            # Stage 6: AI Execution (required)
            current_stage_name = stages[5].stage_name
            result = self._execute_stage(run, stages[5], self._stage_execution)
            if result.failed:
                return self._build_result(run, stages, "failed", pipeline_start)

            # Stage 7: AI Response Intelligence (non-fatal, skippable)
            if not request.skip_validation:
                current_stage_name = stages[6].stage_name
                result = self._execute_stage(run, stages[6], self._stage_validation)
                # Validation failure is non-fatal: pipeline continues
            else:
                # skip_validation=True: Stage 7 marked as "skipped"
                self.pipeline_stage_repo.update_status(
                    stages[6].id, "skipped"
                )
                stages[6].status = "skipped"

            return self._build_result(run, stages, "completed", pipeline_start)

        except Exception as e:
            error = f"Stage {current_stage_name} failed: {str(e)}"
            return self._build_result(run, stages, "failed", pipeline_start, error=error)

    def _execute_stage(
        self,
        run: PipelineRun,
        stage: PipelineStage,
        stage_func: Callable,
    ) -> StageResult:
        """Execute a single pipeline stage with timing and error handling.

        Marks stage as running, calls the stage function, marks completed
        or failed, and records latency.
        """
        # Mark stage running
        self.pipeline_stage_repo.update_status(stage.id, "running")
        stage.status = "running"
        stage.started_at = datetime.utcnow()

        start_time = time.time()

        try:
            stage_func(run, stage)
            latency_ms = (time.time() - start_time) * 1000

            # Mark stage completed
            self.pipeline_stage_repo.update_status(
                stage.id, "completed", latency_ms=latency_ms
            )
            stage.status = "completed"
            stage.latency_ms = latency_ms
            stage.completed_at = datetime.utcnow()

            return StageResult(
                stage_name=stage.stage_name,
                stage_order=stage.stage_order,
                status="completed",
                entity_id=stage.entity_id,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)

            # Mark stage failed
            self.pipeline_stage_repo.update_status(
                stage.id, "failed", latency_ms=latency_ms, error_message=error_msg
            )
            stage.status = "failed"
            stage.latency_ms = latency_ms
            stage.error_message = error_msg
            stage.completed_at = datetime.utcnow()

            # Populate safe diagnostic metadata (no traceback)
            if stage.metadata_ is None:
                stage.metadata_ = {}
            stage.metadata_["error"] = {
                "exception_type": type(e).__name__,
                "stage": stage.stage_name,
                "message": error_msg,
            }

            # Non-fatal stages: record error but don't propagate
            if stage.stage_order in NON_FATAL_STAGES:
                logger.warning(
                    "Stage %s failed (non-fatal, continuing): %s",
                    stage.stage_name,
                    error_msg,
                )
                return StageResult(
                    stage_name=stage.stage_name,
                    stage_order=stage.stage_order,
                    status="failed",
                    entity_id=stage.entity_id,
                    latency_ms=latency_ms,
                    error=error_msg,
                )

            # Required stages: propagate exception
            raise

    def _build_result(
        self,
        run: PipelineRun,
        stages: List[PipelineStage],
        status: str,
        pipeline_start: float,
        error: Optional[str] = None,
    ) -> PipelineResult:
        """Build PipelineResult from current pipeline state."""
        total_latency_ms = (time.time() - pipeline_start) * 1000

        # Update pipeline run status
        self.pipeline_run_repo.update_status(
            run.id, status, total_latency_ms=total_latency_ms, error_message=error
        )

        # Build stage results
        stage_results = [
            StageResult(
                stage_name=s.stage_name,
                stage_order=s.stage_order,
                status=s.status,
                entity_id=s.entity_id,
                latency_ms=s.latency_ms,
                error=s.error_message,
            )
            for s in stages
        ]

        # Extract AI response and validation result from stage metadata
        ai_response = None
        validation_result = None

        # Stage 6 (ai_execution) stores parsed_response in metadata
        if len(stages) > 5 and stages[5].status == "completed":
            meta = stages[5].metadata_ or {}
            ai_response = meta.get("parsed_response")

        # Stage 7 (ai_response_intelligence) stores validation_result in metadata
        if len(stages) > 6 and stages[6].status == "completed":
            meta = stages[6].metadata_ or {}
            validation_result = meta.get("validation_result")

        return PipelineResult(
            pipeline_run_id=run.id,
            status=status,
            stages=stage_results,
            resume_profile_id=run.resume_profile_id,
            opportunity_id=run.opportunity_id,
            gap_analysis_id=run.gap_analysis_id,
            knowledge_retrieval_id=run.knowledge_retrieval_id,
            prompt_package_id=run.prompt_package_id,
            ai_execution_id=run.ai_execution_id,
            ai_validation_id=run.ai_validation_id,
            ai_response=ai_response,
            validation_result=validation_result,
            error=error,
            total_latency_ms=total_latency_ms,
        )

    # ========================================================================
    # Stage Functions
    # ========================================================================

    def _stage_resume_intelligence(self, run: PipelineRun, stage: PipelineStage):
        """Stage 1: Resume Intelligence.

        Creates resume profile and triggers parsing.
        Updates run.resume_profile_id and stage.entity_id.
        """
        # Create resume profile
        profile = self.resume_intelligence_service.create_profile(
            run.user_id,
            ResumeIntelligenceCreate(raw_text=run.resume_text),
        )

        # Trigger parsing
        self.resume_intelligence_service.trigger_parse(profile.id, run.user_id)

        # Store profile ID in pipeline run and stage
        run.resume_profile_id = profile.id
        stage.entity_id = profile.id

    def _stage_opportunity(self, run: PipelineRun, stage: PipelineStage):
        """Stage 2: Opportunity Intelligence.

        Creates opportunity and triggers parsing.
        Updates run.opportunity_id and stage.entity_id.
        """
        # Create opportunity
        opportunity = self.opportunity_service.create_opportunity(
            run.user_id,
            OpportunityCreate(raw_text=run.opportunity_text),
        )

        # Trigger parsing
        self.opportunity_service.trigger_parse(opportunity.id, run.user_id)

        # Store opportunity ID in pipeline run and stage
        run.opportunity_id = opportunity.id
        stage.entity_id = opportunity.id

    def _stage_gap_analysis(self, run: PipelineRun, stage: PipelineStage):
        """Stage 3: Gap Analysis.

        Creates gap analysis and runs analysis.
        Updates run.gap_analysis_id and stage.entity_id.
        """
        # Create gap analysis
        analysis = self.gap_analysis_service.create(
            run.user_id,
            run.resume_profile_id,
            run.opportunity_id,
        )

        # Run analysis
        self.gap_analysis_service.analyze(analysis.id)

        # Store gap analysis ID in pipeline run and stage
        run.gap_analysis_id = analysis.id
        stage.entity_id = analysis.id

    def _stage_knowledge(self, run: PipelineRun, stage: PipelineStage):
        """Stage 4: Knowledge Intelligence (non-fatal).

        Retrieves knowledge rules based on gap analysis.
        Updates run.knowledge_retrieval_id and stage.entity_id.
        Failure is non-fatal: pipeline continues with empty context.
        """
        # Retrieve knowledge
        result = self.knowledge_intelligence_service.retrieve_knowledge(
            run.gap_analysis_id,
            run.user_id,
        )

        # Store knowledge retrieval ID in pipeline run and stage
        retrieval_id = result["retrieval"].id
        run.knowledge_retrieval_id = retrieval_id
        stage.entity_id = retrieval_id

    def _stage_prompt(self, run: PipelineRun, stage: PipelineStage):
        """Stage 5: Prompt Intelligence.

        Builds prompt package from gap analysis and knowledge.
        Updates run.prompt_package_id and stage.entity_id.
        """
        result = self.prompt_intelligence_service.build_prompt(
            run.user_id,
            run.gap_analysis_id,
        )

        package_id = result["package"].id
        run.prompt_package_id = package_id
        stage.entity_id = package_id

    def _stage_execution(self, run: PipelineRun, stage: PipelineStage):
        """Stage 6: AI Execution.

        Executes prompt package against AI provider.
        Updates run.ai_execution_id and stage.entity_id.
        """
        result = self.ai_execution_service.execute_prompt_package(
            run.user_id,
            run.prompt_package_id,
        )

        execution_id = result["execution_id"]
        run.ai_execution_id = execution_id
        stage.entity_id = execution_id
        stage.metadata_["parsed_response"] = result.get("parsed_response")

    def _stage_validation(self, run: PipelineRun, stage: PipelineStage):
        """Stage 7: AI Response Intelligence (non-fatal, skippable).

        Validates AI response against truth, knowledge, and gap analysis.
        Updates run.ai_validation_id and stage.entity_id.
        Failure is non-fatal: pipeline continues.
        """
        result = self.ai_response_intelligence_service.validate_ai_response(
            run.user_id,
            run.ai_execution_id,
        )

        validation_id = result["validation_id"]
        run.ai_validation_id = validation_id
        stage.entity_id = validation_id
        stage.metadata_["validation_result"] = result.get("validation_result")

    # ========================================================================
    # Status Retrieval (Task 4.1)
    # ========================================================================

    def get_pipeline_status(self, pipeline_run_id: str) -> PipelineResult:
        """Retrieve pipeline status and stage information.

        Loads PipelineRun + PipelineStage records from DB and constructs
        PipelineResult with per-stage status.

        Returns PipelineResult with status="failed" and error message if
        the pipeline run does not exist.
        """
        run = self.pipeline_run_repo.get_by_id(pipeline_run_id)

        if not run:
            return PipelineResult(
                pipeline_run_id=pipeline_run_id,
                status="failed",
                stages=[],
                error=f"Pipeline run not found: {pipeline_run_id}",
            )

        stages = self.pipeline_stage_repo.get_by_run_id(pipeline_run_id)

        stage_results = [
            StageResult(
                stage_name=s.stage_name,
                stage_order=s.stage_order,
                status=s.status,
                entity_id=s.entity_id,
                latency_ms=s.latency_ms,
                error=s.error_message,
                metadata=s.metadata_ or {},
            )
            for s in stages
        ]

        return PipelineResult(
            pipeline_run_id=run.id,
            status=run.status,
            stages=stage_results,
            resume_profile_id=run.resume_profile_id,
            opportunity_id=run.opportunity_id,
            gap_analysis_id=run.gap_analysis_id,
            knowledge_retrieval_id=run.knowledge_retrieval_id,
            prompt_package_id=run.prompt_package_id,
            ai_execution_id=run.ai_execution_id,
            ai_validation_id=run.ai_validation_id,
            ai_response=None,
            validation_result=None,
            error=run.error_message,
            total_latency_ms=run.total_latency_ms or 0.0,
        )

    # ========================================================================
    # Pipeline Run Listing (Task 4.2)
    # ========================================================================

    def list_pipeline_runs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[PipelineResult]:
        """List pipeline runs for a user with pagination.

        Returns PipelineRun records ordered by created_at DESC, each
        with its stages mapped to StageResult records.
        """
        runs, _ = self.pipeline_run_repo.get_by_user_id(
            user_id, skip=skip, limit=limit
        )

        results = []
        for run in runs:
            stages = self.pipeline_stage_repo.get_by_run_id(run.id)

            stage_results = [
                StageResult(
                    stage_name=s.stage_name,
                    stage_order=s.stage_order,
                    status=s.status,
                    entity_id=s.entity_id,
                    latency_ms=s.latency_ms,
                    error=s.error_message,
                    metadata=s.metadata_ or {},
                )
                for s in stages
            ]

            results.append(PipelineResult(
                pipeline_run_id=run.id,
                status=run.status,
                stages=stage_results,
                resume_profile_id=run.resume_profile_id,
                opportunity_id=run.opportunity_id,
                gap_analysis_id=run.gap_analysis_id,
                knowledge_retrieval_id=run.knowledge_retrieval_id,
                prompt_package_id=run.prompt_package_id,
                ai_execution_id=run.ai_execution_id,
                ai_validation_id=run.ai_validation_id,
                ai_response=None,
                validation_result=None,
                error=run.error_message,
                total_latency_ms=run.total_latency_ms or 0.0,
            ))

        return results
