"""Type definitions for the Intelligence Pipeline.

Defines the pipeline contract:
- PipelineRequest (input)
- PipelineResult (output)
- StageResult (per-stage output)
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PipelineRequest:
    """Input to Intelligence Pipeline.

    Caller provides resume text + opportunity text.
    user_id is NOT part of this request — it comes from the authenticated
    request context via Depends(require_auth) and is passed as a separate
    parameter to execute_pipeline().
    """
    resume_text: str
    opportunity_text: str
    skip_validation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StageResult:
    """Result from a single pipeline stage.

    Tracks per-stage status, entity ID produced, timing, and error info.
    """
    stage_name: str
    stage_order: int
    status: str  # "pending" | "running" | "completed" | "failed" | "skipped"
    entity_id: Optional[str] = None
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def failed(self) -> bool:
        return self.status == "failed"

    @property
    def completed(self) -> bool:
        return self.status == "completed"


@dataclass
class PipelineResult:
    """Output from Intelligence Pipeline.

    Contains all entity IDs produced by the pipeline, the AI response,
    validation result, and per-stage status.
    """
    pipeline_run_id: str
    status: str  # "completed" | "failed"
    stages: List[StageResult]
    resume_profile_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    gap_analysis_id: Optional[str] = None
    knowledge_retrieval_id: Optional[str] = None
    prompt_package_id: Optional[str] = None
    ai_execution_id: Optional[str] = None
    ai_validation_id: Optional[str] = None
    ai_response: Optional[Dict] = None
    validation_result: Optional[Dict] = None
    error: Optional[str] = None
    total_latency_ms: float = 0.0
