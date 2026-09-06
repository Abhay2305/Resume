"""Metrics domain schemas.

Pydantic models for metrics API request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Valid metric names (allowlist)
# ---------------------------------------------------------------------------

VALID_METRIC_NAMES: frozenset = frozenset({
    "request_count",
    "response_time",
    "error_count",
    "ai_tokens",
    "ai_cost",
    "job_execution",
    "job_duration",
})


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class MetricOut(BaseModel):
    """Single metric sample output."""
    id: str
    metric_name: str
    metric_value: float
    dimensions: Optional[Dict[str, Any]] = None
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricListResponse(BaseModel):
    """Paginated metric list response."""
    items: List[MetricOut]
    total: int
    page: int
    size: int


class MetricSummary(BaseModel):
    """Aggregated metrics summary for a time period."""
    request_count: int
    avg_response_time_ms: float
    error_rate: float
    ai_tokens_total: int
    ai_cost_total: float
    period_start: datetime
    period_end: datetime


class FlushResponse(BaseModel):
    """Response from manual flush endpoint."""
    flushed: int


class CleanupResponse(BaseModel):
    """Response from manual cleanup endpoint."""
    deleted: int
