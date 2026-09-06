"""Pipeline Intelligence Engine API router.

Provides endpoints for executing the intelligence pipeline and retrieving
pipeline status and stage information.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_auth
from app.repositories.pipeline import PipelineRunRepository, PipelineStageRepository
from app.schemas.pipeline import (
    PipelineExecuteRequest,
    PipelineRunResponse,
    PipelineRunListOut,
    PipelineRunListResponse,
    PipelineStageResponse,
)
from app.services.intelligence_pipeline.service import IntelligencePipelineService
from app.services.intelligence_pipeline.types import PipelineRequest
from app.services.resume_intelligence.service import ResumeIntelligenceService
from app.services.opportunity.service import OpportunityService
from app.services.gap_analysis.service import GapAnalysisService
from app.services.knowledge_intelligence.service import KnowledgeIntelligenceService
from app.services.prompt_intelligence.service import PromptIntelligenceService
from app.services.ai_execution.service import AIExecutionService
from app.services.ai_response_intelligence.service import AIResponseIntelligenceService

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


def _build_service(db: Session) -> IntelligencePipelineService:
    """Construct IntelligencePipelineService with all dependencies."""
    return IntelligencePipelineService(
        db=db,
        resume_intelligence_service=ResumeIntelligenceService(db),
        opportunity_service=OpportunityService(db),
        gap_analysis_service=GapAnalysisService(db),
        knowledge_intelligence_service=KnowledgeIntelligenceService(db),
        prompt_intelligence_service=PromptIntelligenceService(db),
        ai_execution_service=AIExecutionService(db),
        ai_response_intelligence_service=AIResponseIntelligenceService(db),
        pipeline_run_repo=PipelineRunRepository(db),
        pipeline_stage_repo=PipelineStageRepository(db),
    )


@router.post("/execute", response_model=PipelineRunResponse, status_code=201)
async def execute_pipeline(
    data: PipelineExecuteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Execute the full intelligence pipeline.

    Creates and runs a 7-stage pipeline: Resume Intelligence, Opportunity
    Intelligence, Gap Analysis, Knowledge Intelligence, Prompt Intelligence,
    AI Execution, and AI Response Intelligence.

    Requires authentication. The pipeline runs as the authenticated user.
    """
    service = _build_service(db)

    try:
        request = PipelineRequest(
            resume_text=data.resume_text,
            opportunity_text=data.opportunity_text,
            skip_validation=data.skip_validation,
            metadata=data.metadata,
        )
        result = service.execute_pipeline(request, current_user.id)
        return PipelineRunResponse(
            pipeline_run_id=result.pipeline_run_id,
            status=result.status,
            stages=[PipelineStageResponse(
                stage_name=s.stage_name,
                stage_order=s.stage_order,
                status=s.status,
                entity_id=s.entity_id,
                latency_ms=s.latency_ms,
                error=s.error,
                metadata=s.metadata,
            ) for s in result.stages],
            resume_profile_id=result.resume_profile_id,
            opportunity_id=result.opportunity_id,
            gap_analysis_id=result.gap_analysis_id,
            knowledge_retrieval_id=result.knowledge_retrieval_id,
            prompt_package_id=result.prompt_package_id,
            ai_execution_id=result.ai_execution_id,
            ai_validation_id=result.ai_validation_id,
            ai_response=result.ai_response,
            validation_result=result.validation_result,
            error=result.error,
            total_latency_ms=result.total_latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/runs", response_model=PipelineRunListResponse)
async def list_pipeline_runs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """List pipeline runs for the authenticated user.

    Returns paginated pipeline runs with preview text from resume and
    opportunity inputs.

    Requires authentication. Users can only see their own pipeline runs.
    """
    service = _build_service(db)
    skip = (page - 1) * size
    results = service.list_pipeline_runs(current_user.id, skip=skip, limit=size)

    items = []
    for result in results:
        items.append(PipelineRunListOut(
            id=result.pipeline_run_id,
            status=result.status,
            resume_text_preview=None,
            opportunity_text_preview=None,
            total_latency_ms=result.total_latency_ms,
            error=result.error,
        ))

    # Get total count for pagination (repo returns count with any limit)
    run_repo = PipelineRunRepository(db)
    _, total = run_repo.get_by_user_id(current_user.id, skip=0, limit=1)

    return PipelineRunListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.get("/{pipeline_run_id}", response_model=PipelineRunResponse)
async def get_pipeline_status(
    pipeline_run_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get pipeline status and stage information.

    Returns the full pipeline result including all entity IDs, stage
    statuses, and error information.

    Requires authentication. Users can only access their own pipelines.
    """
    run_repo = PipelineRunRepository(db)

    run = run_repo.get_by_id(pipeline_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    if run.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    service = _build_service(db)
    result = service.get_pipeline_status(pipeline_run_id)

    return PipelineRunResponse(
        pipeline_run_id=result.pipeline_run_id,
        status=result.status,
        stages=[PipelineStageResponse(
            stage_name=s.stage_name,
            stage_order=s.stage_order,
            status=s.status,
            entity_id=s.entity_id,
            latency_ms=s.latency_ms,
            error=s.error,
            metadata=s.metadata,
        ) for s in result.stages],
        resume_profile_id=result.resume_profile_id,
        opportunity_id=result.opportunity_id,
        gap_analysis_id=result.gap_analysis_id,
        knowledge_retrieval_id=result.knowledge_retrieval_id,
        prompt_package_id=result.prompt_package_id,
        ai_execution_id=result.ai_execution_id,
        ai_validation_id=result.ai_validation_id,
        ai_response=result.ai_response,
        validation_result=result.validation_result,
        error=result.error,
        total_latency_ms=result.total_latency_ms,
    )


@router.get("/{pipeline_run_id}/stages", response_model=list[PipelineStageResponse])
async def get_pipeline_stages(
    pipeline_run_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get pipeline stage information only.

    Returns only the stage results without the full pipeline metadata.

    Requires authentication. Users can only access their own pipelines.
    """
    run_repo = PipelineRunRepository(db)

    run = run_repo.get_by_id(pipeline_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    if run.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    service = _build_service(db)
    result = service.get_pipeline_status(pipeline_run_id)

    return [PipelineStageResponse(
        stage_name=s.stage_name,
        stage_order=s.stage_order,
        status=s.status,
        entity_id=s.entity_id,
        latency_ms=s.latency_ms,
        error=s.error,
        metadata=s.metadata,
    ) for s in result.stages]
