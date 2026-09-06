"""AI Monitoring schemas.

Response models for admin AI monitoring endpoints.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class AiTokenModelBreakdown(BaseModel):
    """Token usage breakdown by model."""
    model: str
    tokens: int
    percentage: float


class AiTokenResponse(BaseModel):
    """Token usage analytics response."""
    total_tokens: int
    by_model: List[AiTokenModelBreakdown]
    daily_trend: List[Dict[str, Any]]
    avg_tokens_per_request: float
    period: str


class AiExecutionStatsResponse(BaseModel):
    """Execution statistics response."""
    total_executions: int
    success_rate: float
    failure_rate: float
    avg_latency_ms: float
    total_retries: int
    by_status: Dict[str, int]
    daily_trend: List[Dict[str, Any]]


class AiProviderModelStats(BaseModel):
    """Per-model stats for a provider."""
    model: str
    executions: int
    tokens: int


class AiProviderDetail(BaseModel):
    """Provider health and usage detail."""
    name: str
    healthy: bool
    total_executions: int
    success_rate: float
    avg_latency_ms: float
    total_cost: float
    total_tokens: int
    models: List[AiProviderModelStats]


class AiProviderStatsResponse(BaseModel):
    """Provider stats response."""
    providers: List[AiProviderDetail]
