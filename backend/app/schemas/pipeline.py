"""Pipeline Intelligence Engine schemas.

Pydantic models for pipeline API request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Request Schemas
# ============================================================================

class PipelineExecuteRequest(BaseModel):
    """Request to execute the full intelligence pipeline.

    user_id is NOT part of this request — it comes from the authenticated
    request context via Depends(require_auth).
    """
    resume_text: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="Raw resume content",
    )
    opportunity_text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Raw job description content",
    )
    skip_validation: bool = Field(
        default=False,
        description="Skip AI Response Intelligence validation (Stage 7)",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional pipeline metadata",
    )


# ============================================================================
# Response Schemas
# ============================================================================

class PipelineStageResponse(BaseModel):
    """Single pipeline stage result."""
    stage_name: str
    stage_order: int
    status: str  # "pending" | "running" | "completed" | "failed" | "skipped"
    entity_id: Optional[str] = None
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class PipelineRunResponse(BaseModel):
    """Pipeline execution result."""
    pipeline_run_id: str
    status: str  # "completed" | "failed"
    stages: List[PipelineStageResponse]
    resume_profile_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    gap_analysis_id: Optional[str] = None
    knowledge_retrieval_id: Optional[str] = None
    prompt_package_id: Optional[str] = None
    ai_execution_id: Optional[str] = None
    ai_validation_id: Optional[str] = None
    ai_response: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    total_latency_ms: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PipelineRunListOut(BaseModel):
    """Pipeline run list item for listing endpoints."""
    id: str
    status: str
    resume_text_preview: Optional[str] = None
    opportunity_text_preview: Optional[str] = None
    total_latency_ms: float = 0.0
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PipelineRunListResponse(BaseModel):
    """Paginated pipeline run list response."""
    items: List[PipelineRunListOut]
    total: int
    page: int
    size: int
