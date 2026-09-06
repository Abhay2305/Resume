"""Integration tests for TokenBudget in UniversalAIService (Task 3.1)."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService
from app.services.ai.error_classifier import TokenBudgetExceeded
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType


def _config(**overrides):
    defaults = dict(
        provider_type=ProviderType.OPENAI,
        api_key="test-key",
        model="gpt-4o-mini",
        max_retries=0,
        retry_base_delay=0.01,
    )
    defaults.update(overrides)
    return ProviderConfig(**defaults)


def _mock_response(content="Hello", prompt_tokens=10, completion_tokens=5):
    return ProviderResponse(
        content=content,
        model="gpt-4o-mini",
        provider=ProviderType.OPENAI,
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        finish_reason="stop",
        latency_ms=50.0,
    )


def _mock_provider(response=None):
    provider = MagicMock()
    provider.generate = AsyncMock(return_value=response or _mock_response())
    provider.health_check = AsyncMock(return_value=True)
    return provider


class TestTokenBudgetIntegration:
    """Test 1: Request-level budget enforced — input token limit."""

    @pytest.mark.asyncio
    async def test_request_level_budget_enforced(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "10")
        service = UniversalAIService(config=_config())

        with pytest.raises(TokenBudgetExceeded, match="Input token estimate"):
            await service.generate([{"role": "user", "content": "a" * 100}])

    """Test 2: Per-user daily budget enforced when user_id provided."""

    @pytest.mark.asyncio
    async def test_per_user_daily_budget_enforced(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "50")
        service = UniversalAIService(config=_config())

        # First request uses some budget
        provider = _mock_provider(response=_mock_response(prompt_tokens=10, completion_tokens=5))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            await service.generate(
                [{"role": "user", "content": "Hello"}],
                user_id="user-1",
            )

        # Second request should exceed daily limit (estimated tokens > remaining)
        with pytest.raises(TokenBudgetExceeded, match="daily token limit"):
            await service.generate(
                [{"role": "user", "content": "a" * 200}],
                user_id="user-1",
            )

    """Test 3: Per-user daily budget skipped when user_id is None."""

    @pytest.mark.asyncio
    async def test_per_user_budget_skipped_when_no_user_id(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "10")
        service = UniversalAIService(config=_config())

        provider = _mock_provider()
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            # Large content but no user_id → daily budget not checked
            response = await service.generate(
                [{"role": "user", "content": "a" * 200}],
                user_id=None,
            )
            assert response.content == "Hello"

    """Test 4: Per-user monthly budget enforced when user_id provided."""

    @pytest.mark.asyncio
    async def test_per_user_monthly_budget_enforced(self, monkeypatch):
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "50")
        service = UniversalAIService(config=_config())

        provider = _mock_provider(response=_mock_response(prompt_tokens=10, completion_tokens=5))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            await service.generate(
                [{"role": "user", "content": "Hello"}],
                user_id="user-1",
            )

        with pytest.raises(TokenBudgetExceeded, match="monthly token limit"):
            await service.generate(
                [{"role": "user", "content": "a" * 200}],
                user_id="user-1",
            )

    """Test 5: Streaming budget check before stream starts."""

    @pytest.mark.asyncio
    async def test_streaming_budget_check_enforced(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "10")
        service = UniversalAIService(config=_config())

        with pytest.raises(TokenBudgetExceeded, match="Input token estimate"):
            async for _ in service.generate_stream([{"role": "user", "content": "a" * 100}]):
                pass

    """Test 6: Streaming per-user budget enforced."""

    @pytest.mark.asyncio
    async def test_streaming_per_user_budget_enforced(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "50")
        service = UniversalAIService(config=_config())

        provider = _mock_provider()
        # Use up budget first via generate()
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            await service.generate(
                [{"role": "user", "content": "Hello"}],
                user_id="user-1",
            )

        with pytest.raises(TokenBudgetExceeded, match="daily token limit"):
            async for _ in service.generate_stream(
                [{"role": "user", "content": "a" * 200}],
                user_id="user-1",
            ):
                pass

    """Test 7: Streaming per-user budget skipped when user_id is None."""

    @pytest.mark.asyncio
    async def test_streaming_no_user_id_skips_budget(self, monkeypatch):
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "10")
        service = UniversalAIService(config=_config())

        async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
            yield "token1"
            yield "token2"

        provider = MagicMock()
        provider.generate_stream = mock_stream

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream(
                [{"role": "user", "content": "a" * 200}],
                user_id=None,
            ):
                tokens.append(token)
            assert tokens == ["token1", "token2"]

    """Test 8: Budget limits zero means unlimited."""

    @pytest.mark.asyncio
    async def test_zero_budget_means_unlimited(self, monkeypatch):
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "0")
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "0")
        monkeypatch.setenv("AI_USER_MONTHLY_TOKEN_LIMIT", "0")
        service = UniversalAIService(config=_config())

        provider = _mock_provider()
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            response = await service.generate(
                [{"role": "user", "content": "a" * 10000}],
                user_id="user-1",
            )
            assert response.content == "Hello"
