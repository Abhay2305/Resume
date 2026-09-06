"""Tests for TokenBudget."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.services.ai.error_classifier import TokenBudgetExceeded
from app.services.ai.token_budget import TokenBudget


class TestTokenBudget:
    def test_estimate_tokens(self):
        budget = TokenBudget()
        assert budget.estimate_tokens("hello") == 1
        assert budget.estimate_tokens("helloworld") == 2
        assert budget.estimate_tokens("12345678") == 2

    def test_check_input_within_limit(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "100")
        budget = TokenBudget()
        budget.check_input("a" * 400)  # 100 tokens

    def test_check_input_exceeds_limit(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "10")
        budget = TokenBudget()
        with pytest.raises(TokenBudgetExceeded, match="Input token estimate"):
            budget.check_input("a" * 100)  # 25 tokens

    def test_check_input_unlimited(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "0")
        budget = TokenBudget()
        budget.check_input("a" * 10000)  # no limit

    def test_check_user_daily_within_limit(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "1000")
        budget = TokenBudget()
        budget.check_user_daily("user-1", 500)

    def test_check_user_daily_exceeds_limit(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "100")
        budget = TokenBudget()
        budget.record_usage("user-1", 90)
        with pytest.raises(TokenBudgetExceeded, match="daily token limit"):
            budget.check_user_daily("user-1", 20)

    def test_check_user_daily_unlimited(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "0")
        budget = TokenBudget()
        budget.check_user_daily("user-1", 999999)

    def test_check_user_monthly_within_limit(self, monkeypatch):
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "10000")
        budget = TokenBudget()
        budget.check_user_monthly("user-1", 5000)

    def test_check_user_monthly_exceeds_limit(self, monkeypatch):
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "100")
        budget = TokenBudget()
        budget.record_usage("user-1", 90)
        with pytest.raises(TokenBudgetExceeded, match="monthly token limit"):
            budget.check_user_monthly("user-1", 20)

    def test_check_user_monthly_unlimited(self, monkeypatch):
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "0")
        budget = TokenBudget()
        budget.check_user_monthly("user-1", 999999)

    def test_get_budget_status_no_user(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "8000")
        budget = TokenBudget()
        status = budget.get_budget_status()
        assert status["max_input_tokens"] == 8000

    def test_get_budget_status_with_user(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "1000")
        budget = TokenBudget()
        budget.record_usage("user-1", 300)
        status = budget.get_budget_status("user-1")
        assert status["user_daily_used"] == 300
        assert status["user_daily_remaining"] == 700

    def test_get_budget_usage(self, monkeypatch):
        budget = TokenBudget()
        budget.record_usage("user-1", 500)
        usage = budget.get_budget_usage("user-1")
        assert usage["daily_tokens"] == 500
        assert usage["monthly_tokens"] == 500

    def test_get_budget_usage_no_user(self):
        budget = TokenBudget()
        assert budget.get_budget_usage() == {}


class TestTokenBudgetMonitoring:
    """Task 3.2: Budget monitoring — cumulative tracking, status, and reset."""

    def test_budget_status_accurate_after_multiple_requests(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "1000")
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "10000")
        budget = TokenBudget()

        budget.record_usage("user-1", 200)
        status = budget.get_budget_status("user-1")
        assert status["user_daily_used"] == 200
        assert status["user_daily_remaining"] == 800
        assert status["user_monthly_used"] == 200
        assert status["user_monthly_remaining"] == 9800

        budget.record_usage("user-1", 300)
        status = budget.get_budget_status("user-1")
        assert status["user_daily_used"] == 500
        assert status["user_daily_remaining"] == 500
        assert status["user_monthly_used"] == 500
        assert status["user_monthly_remaining"] == 9500

        budget.record_usage("user-1", 400)
        status = budget.get_budget_status("user-1")
        assert status["user_daily_used"] == 900
        assert status["user_daily_remaining"] == 100
        assert status["user_monthly_used"] == 900
        assert status["user_monthly_remaining"] == 9100

    def test_budget_status_multiple_users_independent(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "1000")
        budget = TokenBudget()

        budget.record_usage("user-1", 500)
        budget.record_usage("user-2", 300)

        s1 = budget.get_budget_status("user-1")
        s2 = budget.get_budget_status("user-2")
        assert s1["user_daily_used"] == 500
        assert s2["user_daily_used"] == 300
        assert s1["user_daily_remaining"] == 500
        assert s2["user_daily_remaining"] == 700

    def test_daily_budget_resets_on_new_day(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "1000")
        budget = TokenBudget()

        mock_dt_day1 = MagicMock()
        mock_dt_day1.strftime.side_effect = lambda fmt: "2025-07-15" if fmt == "%Y-%m-%d" else "2025-07"
        with patch("app.services.ai.token_budget.datetime") as mock_dt:
            mock_dt.now.return_value = mock_dt_day1
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            budget.record_usage("user-1", 800)
            status_day1 = budget.get_budget_status("user-1")

        assert status_day1["user_daily_used"] == 800
        assert status_day1["user_daily_remaining"] == 200

        mock_dt_day2 = MagicMock()
        mock_dt_day2.strftime.side_effect = lambda fmt: "2025-07-16" if fmt == "%Y-%m-%d" else "2025-07"
        with patch("app.services.ai.token_budget.datetime") as mock_dt:
            mock_dt.now.return_value = mock_dt_day2
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            budget.record_usage("user-1", 100)
            status_day2 = budget.get_budget_status("user-1")

        assert status_day2["user_daily_used"] == 100
        assert status_day2["user_daily_remaining"] == 900
        assert status_day2["user_monthly_used"] == 900

    def test_monthly_budget_resets_on_new_month(self, monkeypatch):
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "5000")
        budget = TokenBudget()

        mock_dt_jun = MagicMock()
        mock_dt_jun.strftime.side_effect = lambda fmt: "2025-06-30" if fmt == "%Y-%m-%d" else "2025-06"
        with patch("app.services.ai.token_budget.datetime") as mock_dt:
            mock_dt.now.return_value = mock_dt_jun
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            budget.record_usage("user-1", 4000)
            status_jun = budget.get_budget_status("user-1")

        assert status_jun["user_monthly_used"] == 4000
        assert status_jun["user_monthly_remaining"] == 1000

        mock_dt_jul = MagicMock()
        mock_dt_jul.strftime.side_effect = lambda fmt: "2025-07-01" if fmt == "%Y-%m-%d" else "2025-07"
        with patch("app.services.ai.token_budget.datetime") as mock_dt:
            mock_dt.now.return_value = mock_dt_jul
            mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
            budget.record_usage("user-1", 500)
            status_jul = budget.get_budget_status("user-1")

        assert status_jul["user_monthly_used"] == 500
        assert status_jul["user_monthly_remaining"] == 4500
        assert status_jul["user_daily_used"] == 500

    def test_budget_usage_tracks_cumulative(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "5000")
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "50000")
        budget = TokenBudget()

        for _ in range(5):
            budget.record_usage("user-1", 100)

        usage = budget.get_budget_usage("user-1")
        assert usage["daily_tokens"] == 500
        assert usage["monthly_tokens"] == 500

    def test_get_metrics_summary_includes_budget(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "8000")
        monkeypatch.setenv("AI_MAX_OUTPUT_TOKENS", "8192")
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "100000")
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "1000000")
        from app.services.ai.universal_service import UniversalAIService
        from app.services.ai.types import ProviderConfig, ProviderType, ProviderMetrics

        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
            )
        )
        m = ProviderMetrics(provider="openai", total_tokens=100, success=True)
        service._cost_tracker.record(m)

        summary = service.get_metrics_summary()
        assert "budget" in summary
        assert summary["budget"]["max_input_tokens"] == 8000
        assert summary["budget"]["max_output_tokens"] == 8192
        assert summary["budget"]["user_daily_limit"] == 100000
        assert summary["budget"]["user_monthly_limit"] == 1000000

    def test_budget_exhausted_blocks_new_requests(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "100")
        budget = TokenBudget()

        budget.record_usage("user-1", 100)

        with pytest.raises(TokenBudgetExceeded, match="daily token limit"):
            budget.check_user_daily("user-1", 1)

        usage = budget.get_budget_usage("user-1")
        assert usage["daily_tokens"] == 100
