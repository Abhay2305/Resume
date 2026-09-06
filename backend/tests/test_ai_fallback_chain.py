"""Integration tests for the fallback chain logic (Task 2.1)."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService
from app.services.ai.error_classifier import (
    AuthenticationError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType


def _config(provider_type=ProviderType.OPENAI, model="gpt-4o-mini", **overrides):
    defaults = dict(
        provider_type=provider_type,
        api_key="test-key",
        model=model,
        max_retries=0,
        retry_base_delay=0.01,
        retry_max_delay=0.1,
    )
    defaults.update(overrides)
    return ProviderConfig(**defaults)


def _gemini_config(**overrides):
    return _config(provider_type=ProviderType.GEMINI, model="gemini-2.0-flash", **overrides)


def _anthropic_config(**overrides):
    return _config(provider_type=ProviderType.ANTHROPIC, model="claude-3-haiku", **overrides)


def _mock_response(content="Hello", model="gpt-4o-mini", provider=ProviderType.OPENAI,
                    prompt_tokens=10, completion_tokens=5):
    return ProviderResponse(
        content=content,
        model=model,
        provider=provider,
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        finish_reason="stop",
        latency_ms=50.0,
    )


def _mock_provider(response=None, side_effect=None):
    provider = MagicMock()
    if side_effect:
        provider.generate = AsyncMock(side_effect=side_effect)
    else:
        provider.generate = AsyncMock(return_value=response or _mock_response())
    provider.health_check = AsyncMock(return_value=True)
    return provider


class TestFallbackChain:
    """Test 1: Primary provider succeeds — no fallback needed."""

    @pytest.mark.asyncio
    async def test_primary_succeeds_no_fallback(self):
        config = _config()
        service = UniversalAIService(config=config)
        # Add a fallback provider to the chain to ensure it's NOT called
        fallback_config = _gemini_config()
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        primary_provider = _mock_provider(response=_mock_response(provider=ProviderType.OPENAI))
        fallback_provider = _mock_provider()

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return primary_provider
                return fallback_provider
            mock_factory.create.side_effect = create_side_effect

            response = await service.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Hello"
            assert response.provider == ProviderType.OPENAI
            assert primary_provider.generate.call_count == 1
            assert fallback_provider.generate.call_count == 0

    """Test 2: Primary fails transiently → retry → succeeds."""

    @pytest.mark.asyncio
    async def test_transient_failure_retry_succeeds(self):
        config = _config(max_retries=2, retry_base_delay=0.01, retry_max_delay=0.1)
        service = UniversalAIService(config=config)

        provider = MagicMock()
        provider.generate = AsyncMock(side_effect=[
            ProviderUnavailableError("503 Service unavailable"),
            _mock_response(provider=ProviderType.OPENAI),
        ])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider

            response = await service.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Hello"
            assert provider.generate.call_count == 2

    """Test 3: Primary fails → retry exhausted → fallback succeeds."""

    @pytest.mark.asyncio
    async def test_retry_exhausted_fallback_succeeds(self):
        config = _config(max_retries=1, retry_base_delay=0.01, retry_max_delay=0.1)
        service = UniversalAIService(config=config)

        fallback_config = _gemini_config()
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        primary_provider = _mock_provider(
            side_effect=ProviderUnavailableError("503 down")
        )
        fallback_provider = _mock_provider(
            response=_mock_response(content="Fallback hello", model="gemini-2.0-flash", provider=ProviderType.GEMINI)
        )

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return primary_provider
                return fallback_provider
            mock_factory.create.side_effect = create_side_effect

            response = await service.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Fallback hello"
            assert response.provider == ProviderType.GEMINI
            # Primary retried once (max_retries=1 → 2 attempts), then fallback
            assert primary_provider.generate.call_count == 2
            assert fallback_provider.generate.call_count == 1

    """Test 4: Primary auth failure → no retry → fallback."""

    @pytest.mark.asyncio
    async def test_auth_error_no_retry_fallback(self):
        config = _config(max_retries=3)
        service = UniversalAIService(config=config)

        fallback_config = _gemini_config()
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        primary_provider = _mock_provider(
            side_effect=AuthenticationError("Invalid key")
        )
        fallback_provider = _mock_provider(
            response=_mock_response(content="Fallback ok", model="gemini-2.0-flash", provider=ProviderType.GEMINI)
        )

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return primary_provider
                return fallback_provider
            mock_factory.create.side_effect = create_side_effect

            response = await service.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Fallback ok"
            # Auth error is non-retryable → 1 attempt only
            assert primary_provider.generate.call_count == 1
            assert fallback_provider.generate.call_count == 1

    """Test 5: Multiple providers fail → next is attempted."""

    @pytest.mark.asyncio
    async def test_multiple_providers_fail_next_attempted(self):
        config = _config(max_retries=0)
        service = UniversalAIService(config=config)

        gemini_cfg = _gemini_config()
        anthropic_cfg = _anthropic_config()
        service._registry.register(ProviderType.GEMINI, gemini_cfg)
        service._registry.register(ProviderType.ANTHROPIC, anthropic_cfg)
        service._fallback_chain = service._registry.get_fallback_chain()

        openai_prov = _mock_provider(side_effect=ProviderUnavailableError("openai down"))
        gemini_prov = _mock_provider(side_effect=ProviderUnavailableError("gemini down"))
        anthropic_prov = _mock_provider(
            response=_mock_response(content="Anthropic ok", model="claude-3-haiku", provider=ProviderType.ANTHROPIC)
        )

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return openai_prov
                if cfg.provider_type == ProviderType.GEMINI:
                    return gemini_prov
                return anthropic_prov
            mock_factory.create.side_effect = create_side_effect

            response = await service.generate([{"role": "user", "content": "Hello"}])

            assert response.content == "Anthropic ok"
            assert response.provider == ProviderType.ANTHROPIC
            assert openai_prov.generate.call_count == 1
            assert gemini_prov.generate.call_count == 1
            assert anthropic_prov.generate.call_count == 1

    """Test 6: All providers fail → aggregated error."""

    @pytest.mark.asyncio
    async def test_all_providers_fail_aggregated_error(self):
        config = _config(max_retries=0)
        service = UniversalAIService(config=config)

        gemini_cfg = _gemini_config()
        service._registry.register(ProviderType.GEMINI, gemini_cfg)
        service._fallback_chain = service._registry.get_fallback_chain()

        openai_prov = _mock_provider(side_effect=ProviderUnavailableError("openai down"))
        gemini_prov = _mock_provider(side_effect=ProviderUnavailableError("gemini down"))

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return openai_prov
                return gemini_prov
            mock_factory.create.side_effect = create_side_effect

            with pytest.raises(ProviderUnavailableError) as exc_info:
                await service.generate([{"role": "user", "content": "Hello"}])

            error_msg = str(exc_info.value)
            assert "All providers exhausted" in error_msg
            assert "openai" in error_msg
            assert "gemini" in error_msg

    """Test 7: Fallback metrics are recorded correctly."""

    @pytest.mark.asyncio
    async def test_fallback_metrics_recorded(self):
        config = _config(max_retries=0)
        service = UniversalAIService(config=config)

        fallback_cfg = _gemini_config()
        service._registry.register(ProviderType.GEMINI, fallback_cfg)
        service._fallback_chain = service._registry.get_fallback_chain()

        primary_prov = _mock_provider(side_effect=ProviderUnavailableError("down"))
        fallback_prov = _mock_provider(
            response=_mock_response(content="ok", model="gemini-2.0-flash", provider=ProviderType.GEMINI)
        )

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return primary_prov
                return fallback_prov
            mock_factory.create.side_effect = create_side_effect

            await service.generate([{"role": "user", "content": "Hello"}])

            fm = service.cost_tracker.fallback_metrics
            assert fm.total_fallbacks >= 1
            # The fallback from openai→gemini should be tracked
            assert fm.by_provider.get("openai", 0) >= 1

    """Test 8: Provider ordering follows ProviderRegistry configuration."""

    @pytest.mark.asyncio
    async def test_provider_ordering_follows_registry(self):
        config = _config(priority=10)
        service = UniversalAIService(config=config)

        gemini_cfg = _gemini_config(priority=5)  # Higher priority (lower number)
        anthropic_cfg = _anthropic_config(priority=20)
        service._registry.register(ProviderType.GEMINI, gemini_cfg)
        service._registry.register(ProviderType.ANTHROPIC, anthropic_cfg)
        service._fallback_chain = service._registry.get_fallback_chain()

        # Chain should be ordered by priority: gemini (5) < openai (10) < anthropic (20)
        chain_types = [c.provider_type for c in service._fallback_chain]
        assert chain_types.index(ProviderType.GEMINI) < chain_types.index(ProviderType.OPENAI)
        assert chain_types.index(ProviderType.OPENAI) < chain_types.index(ProviderType.ANTHROPIC)

    """Test 9: Disabled providers are skipped."""

    @pytest.mark.asyncio
    async def test_disabled_providers_skipped(self):
        config = _config()
        service = UniversalAIService(config=config)

        disabled_gemini = _gemini_config(enabled=False)
        service._registry.register(ProviderType.GEMINI, disabled_gemini)
        service._fallback_chain = service._registry.get_fallback_chain()

        # Disabled gemini should not be in chain
        chain_types = [c.provider_type for c in service._fallback_chain]
        assert ProviderType.GEMINI not in chain_types
        assert ProviderType.OPENAI in chain_types

    """Test 10: Existing Phase 1 tests continue passing (backward compat)."""

    @pytest.mark.asyncio
    async def test_backward_compat_single_provider(self):
        """When no fallback chain is configured, single-provider behavior is preserved."""
        config = _config(max_retries=1, retry_base_delay=0.01, retry_max_delay=0.1)
        service = UniversalAIService(config=config)
        # No additional providers registered — chain is just [openai]

        provider = _mock_provider(response=_mock_response())

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider

            response = await service.generate([{"role": "user", "content": "Hello"}])
            assert response.content == "Hello"
            assert provider.generate.call_count == 1

    @pytest.mark.asyncio
    async def test_backward_compat_metrics_recorded(self):
        """Metrics are still recorded correctly for single-provider flow."""
        config = _config()
        service = UniversalAIService(config=config)

        provider = _mock_provider(response=_mock_response())

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider

            await service.generate([{"role": "user", "content": "test"}])
            history = service.get_metrics_history()
            assert len(history) == 1
            assert history[0].success is True

    @pytest.mark.asyncio
    async def test_auth_error_not_retried_with_fallback(self):
        """Auth error on primary → no retry → fallback to next provider."""
        config = _config(max_retries=3)
        service = UniversalAIService(config=config)

        fallback_cfg = _gemini_config()
        service._registry.register(ProviderType.GEMINI, fallback_cfg)
        service._fallback_chain = service._registry.get_fallback_chain()

        primary = _mock_provider(side_effect=AuthenticationError("Bad key"))
        fallback = _mock_provider(
            response=_mock_response(content="Fallback", model="gemini-2.0-flash", provider=ProviderType.GEMINI)
        )

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_side_effect(cfg):
                if cfg.provider_type == ProviderType.OPENAI:
                    return primary
                return fallback
            mock_factory.create.side_effect = create_side_effect

            response = await service.generate([{"role": "user", "content": "Hello"}])
            assert response.content == "Fallback"
            # Auth error → no retry → 1 attempt
            assert primary.generate.call_count == 1
            assert fallback.generate.call_count == 1
