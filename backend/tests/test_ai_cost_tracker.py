"""Tests for CostTracker, MODEL_COSTS, and estimate_cost."""
import pytest
from app.services.ai.cost_tracker import CostTracker, CostSummary, FallbackMetrics, MODEL_COSTS, estimate_cost
from app.services.ai.types import ProviderMetrics


class TestModelCosts:
    def test_all_models_have_input_and_output(self):
        for model, costs in MODEL_COSTS.items():
            assert "input" in costs, f"{model} missing input cost"
            assert "output" in costs, f"{model} missing output cost"
            assert costs["input"] >= 0
            assert costs["output"] >= 0


class TestEstimateCost:
    def test_gemini_flash_cost(self):
        cost = estimate_cost("gemini-2.0-flash", 1000, 500)
        expected = (1000 / 1_000_000) * 0.10 + (500 / 1_000_000) * 0.40
        assert abs(cost - expected) < 0.0001

    def test_gemini_pro_cost(self):
        cost = estimate_cost("gemini-1.5-pro", 1000, 500)
        expected = (1000 / 1_000_000) * 1.25 + (500 / 1_000_000) * 5.00
        assert abs(cost - expected) < 0.0001

    def test_openai_cost(self):
        cost = estimate_cost("gpt-4o", 1000, 500)
        expected = (1000 / 1_000_000) * 2.50 + (500 / 1_000_000) * 10.00
        assert abs(cost - expected) < 0.0001

    def test_anthropic_cost(self):
        cost = estimate_cost("claude-sonnet-4", 1000, 500)
        expected = (1000 / 1_000_000) * 3.00 + (500 / 1_000_000) * 15.00
        assert abs(cost - expected) < 0.0001

    def test_unknown_model_uses_default(self):
        cost = estimate_cost("unknown-model", 1000, 500)
        expected = (1000 / 1_000_000) * 0.10 + (500 / 1_000_000) * 0.40
        assert abs(cost - expected) < 0.0001

    def test_zero_tokens(self):
        cost = estimate_cost("gemini-2.0-flash", 0, 0)
        assert cost == 0.0


class TestCostTracker:
    def test_record_and_history(self):
        tracker = CostTracker()
        m = ProviderMetrics(provider="openai", model="gpt-4o", total_tokens=100, success=True)
        tracker.record(m)
        assert len(tracker.history()) == 1
        assert tracker.history()[0].provider == "openai"

    def test_history_returns_copy(self):
        tracker = CostTracker()
        tracker.record(ProviderMetrics(provider="openai", total_tokens=10, success=True))
        h = tracker.history()
        h.clear()
        assert len(tracker.history()) == 1

    def test_max_history_capped(self):
        tracker = CostTracker()
        for i in range(1100):
            tracker.record(ProviderMetrics(provider="openai", total_tokens=i, success=True))
        assert len(tracker.history()) <= 1000

    def test_summary_empty(self):
        tracker = CostTracker()
        s = tracker.summary()
        assert s.total_requests == 0

    def test_summary_with_data(self):
        tracker = CostTracker()
        tracker.record(ProviderMetrics(provider="openai", model="gpt-4o", total_tokens=100, estimated_cost=0.001, latency_ms=100, success=True))
        tracker.record(ProviderMetrics(provider="openai", model="gpt-4o", total_tokens=200, estimated_cost=0.002, latency_ms=200, success=True))
        s = tracker.summary()
        assert s.total_requests == 2
        assert s.successful == 2
        assert s.total_tokens == 300
        assert abs(s.total_cost_usd - 0.003) < 0.001
        assert s.average_latency_ms == 150.0

    def test_summary_by_provider(self):
        tracker = CostTracker()
        tracker.record(ProviderMetrics(provider="openai", model="gpt-4o", total_tokens=100, estimated_cost=0.001, success=True))
        tracker.record(ProviderMetrics(provider="gemini", model="gemini-2.0-flash", total_tokens=200, estimated_cost=0.002, success=True))
        s = tracker.summary()
        assert "openai" in s.by_provider
        assert "gemini" in s.by_provider
        assert s.by_provider["openai"]["requests"] == 1
        assert s.by_provider["gemini"]["requests"] == 1

    def test_summary_by_model(self):
        tracker = CostTracker()
        tracker.record(ProviderMetrics(provider="openai", model="gpt-4o", total_tokens=100, success=True))
        tracker.record(ProviderMetrics(provider="openai", model="gpt-4o-mini", total_tokens=50, success=True))
        s = tracker.summary()
        assert "gpt-4o" in s.by_model
        assert "gpt-4o-mini" in s.by_model

    def test_summary_filter_by_provider(self):
        tracker = CostTracker()
        tracker.record(ProviderMetrics(provider="openai", total_tokens=100, success=True))
        tracker.record(ProviderMetrics(provider="gemini", total_tokens=200, success=True))
        s = tracker.summary(provider="openai")
        assert s.total_requests == 1

    def test_fallback_metrics_record(self):
        tracker = CostTracker()
        tracker.record_fallback("openai", "gemini", True)
        tracker.record_fallback("openai", "anthropic", False)
        fm = tracker.fallback_metrics
        assert fm.total_fallbacks == 2
        assert fm.fallbacks_succeeded == 1
        assert fm.by_provider["openai"] == 2
