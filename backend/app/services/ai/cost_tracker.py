"""Cost estimation and tracking for AI provider usage."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.services.ai.types import ProviderMetrics


MODEL_COSTS: Dict[str, Dict[str, float]] = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    costs = MODEL_COSTS.get(model, {"input": 0.10, "output": 0.40})
    input_cost = (prompt_tokens / 1_000_000) * costs["input"]
    output_cost = (completion_tokens / 1_000_000) * costs["output"]
    return round(input_cost + output_cost, 6)


@dataclass
class FallbackMetrics:
    total_fallbacks: int = 0
    fallbacks_succeeded: int = 0
    fallbacks_failed: int = 0
    by_provider: Dict[str, int] = field(default_factory=dict)


@dataclass
class CostSummary:
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    success_rate: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    average_latency_ms: float = 0.0
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_model: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class CostTracker:
    """Tracks per-request costs, aggregates metrics, and tracks fallback usage."""

    MAX_HISTORY = 1000

    def __init__(self):
        self._history: List[ProviderMetrics] = []
        self._fallback_metrics = FallbackMetrics()

    def record(self, metrics: ProviderMetrics) -> None:
        self._history.append(metrics)
        if len(self._history) > self.MAX_HISTORY:
            self._history = self._history[-500:]

    def record_fallback(self, from_provider: str, to_provider: str, succeeded: bool) -> None:
        self._fallback_metrics.total_fallbacks += 1
        if succeeded:
            self._fallback_metrics.fallbacks_succeeded += 1
        self._fallback_metrics.by_provider[from_provider] = (
            self._fallback_metrics.by_provider.get(from_provider, 0) + 1
        )

    def history(self) -> List[ProviderMetrics]:
        return list(self._history)

    def summary(
        self,
        period: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> CostSummary:
        filtered = self._history
        if provider:
            filtered = [m for m in filtered if m.provider == provider]
        if model:
            filtered = [m for m in filtered if m.model == model]

        if not filtered:
            return CostSummary()

        total = len(filtered)
        successful = sum(1 for m in filtered if m.success)
        total_tokens = sum(m.total_tokens for m in filtered)
        total_cost = sum(m.estimated_cost for m in filtered)
        avg_latency = sum(m.latency_ms for m in filtered) / total if total else 0

        by_provider: Dict[str, Dict[str, Any]] = {}
        by_model: Dict[str, Dict[str, Any]] = {}
        for m in filtered:
            if m.provider not in by_provider:
                by_provider[m.provider] = {"requests": 0, "tokens": 0, "cost": 0.0}
            by_provider[m.provider]["requests"] += 1
            by_provider[m.provider]["tokens"] += m.total_tokens
            by_provider[m.provider]["cost"] += m.estimated_cost

            if m.model not in by_model:
                by_model[m.model] = {"requests": 0, "tokens": 0, "cost": 0.0}
            by_model[m.model]["requests"] += 1
            by_model[m.model]["tokens"] += m.total_tokens
            by_model[m.model]["cost"] += m.estimated_cost

        return CostSummary(
            total_requests=total,
            successful=successful,
            failed=total - successful,
            success_rate=round((successful / total) * 100, 2) if total else 0,
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 4),
            average_latency_ms=round(avg_latency, 2),
            by_provider=by_provider,
            by_model=by_model,
        )

    @property
    def fallback_metrics(self) -> FallbackMetrics:
        return self._fallback_metrics
