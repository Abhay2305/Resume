"""Integration tests for streaming in UniversalAIService (Task 5.1)."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService
from app.services.ai.error_classifier import ProviderUnavailableError, ProviderError
from app.services.ai.types import ProviderConfig, ProviderType


def _openai_config(**overrides):
    defaults = dict(
        provider_type=ProviderType.OPENAI,
        api_key="test-key",
        model="gpt-4o-mini",
        max_retries=0,
        retry_base_delay=0.01,
    )
    defaults.update(overrides)
    return ProviderConfig(**defaults)


def _gemini_config(**overrides):
    defaults = dict(
        provider_type=ProviderType.GEMINI,
        api_key="test-key",
        model="gemini-2.0-flash",
        max_retries=0,
        retry_base_delay=0.01,
    )
    defaults.update(overrides)
    return ProviderConfig(**defaults)


def _anthropic_config(**overrides):
    defaults = dict(
        provider_type=ProviderType.ANTHROPIC,
        api_key="test-key",
        model="claude-sonnet-4-20250514",
        max_retries=0,
        retry_base_delay=0.01,
    )
    defaults.update(overrides)
    return ProviderConfig(**defaults)


def _make_streaming_provider(tokens=None):
    if tokens is None:
        tokens = ["Hello", " ", "world"]
    provider = MagicMock()

    async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
        for token in tokens:
            yield token

    provider.generate_stream = mock_stream
    return provider


def _make_failing_streaming_provider(error_msg="Stream failed"):
    provider = MagicMock()

    async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
        raise ProviderError(error_msg, retryable=False)
        yield  # make it an async generator

    provider.generate_stream = mock_stream
    return provider


class TestStreamingIntegration:
    @pytest.mark.asyncio
    async def test_streaming_with_openai_yields_tokens(self):
        service = UniversalAIService(config=_openai_config())
        provider = _make_streaming_provider(["Hello", " ", "from", " OpenAI"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream([{"role": "user", "content": "Hi"}]):
                tokens.append(token)

        assert tokens == ["Hello", " ", "from", " OpenAI"]

    @pytest.mark.asyncio
    async def test_streaming_with_gemini_yields_tokens(self):
        service = UniversalAIService(config=_gemini_config())
        provider = _make_streaming_provider(["Gemini", " ", "response"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream([{"role": "user", "content": "Hi"}]):
                tokens.append(token)

        assert tokens == ["Gemini", " ", "response"]

    @pytest.mark.asyncio
    async def test_streaming_with_anthropic_yields_tokens(self):
        service = UniversalAIService(config=_anthropic_config())
        provider = _make_streaming_provider(["Anthropic", " ", "stream"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream([{"role": "user", "content": "Hi"}]):
                tokens.append(token)

        assert tokens == ["Anthropic", " ", "stream"]

    @pytest.mark.asyncio
    async def test_pre_stream_failure_triggers_fallback(self):
        config = _openai_config()
        service = UniversalAIService(config=config)

        fallback_config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key="test-key",
            model="gemini-2.0-flash",
            max_retries=0,
        )
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        fail_provider = _make_failing_streaming_provider("OpenAI stream failed")
        success_provider = _make_streaming_provider(["Fallback", " ", "success"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_provider(pc):
                if pc.provider_type == ProviderType.OPENAI:
                    return fail_provider
                return success_provider

            mock_factory.create.side_effect = create_provider
            tokens = []
            async for token in service.generate_stream([{"role": "user", "content": "Hi"}]):
                tokens.append(token)

        assert tokens == ["Fallback", " ", "success"]

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_error(self):
        config = _openai_config()
        service = UniversalAIService(config=config)

        fallback_config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key="test-key",
            model="gemini-2.0-flash",
            max_retries=0,
        )
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        fail_provider = _make_failing_streaming_provider("Stream failed")

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = fail_provider
            with pytest.raises(ProviderUnavailableError):
                async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                    pass

    @pytest.mark.asyncio
    async def test_streaming_records_metrics_on_success(self):
        service = UniversalAIService(config=_openai_config())
        provider = _make_streaming_provider(["token"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                pass

        history = service.get_metrics_history()
        assert len(history) == 1
        assert history[0].success is True
        assert history[0].provider == "openai"
        assert history[0].latency_ms >= 0

    @pytest.mark.asyncio
    async def test_streaming_records_metrics_on_failure(self):
        config = _openai_config()
        service = UniversalAIService(config=config)

        fallback_config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key="test-key",
            model="gemini-2.0-flash",
            max_retries=0,
        )
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        fail_provider = _make_failing_streaming_provider("Stream failed")

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = fail_provider
            with pytest.raises(ProviderUnavailableError):
                async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                    pass

        history = service.get_metrics_history()
        assert len(history) == 2
        assert all(m.success is False for m in history)

    @pytest.mark.asyncio
    async def test_streaming_records_fallback_metrics(self):
        config = _openai_config()
        service = UniversalAIService(config=config)

        fallback_config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key="test-key",
            model="gemini-2.0-flash",
            max_retries=0,
        )
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        fail_provider = _make_failing_streaming_provider("OpenAI failed")
        success_provider = _make_streaming_provider(["ok"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            def create_provider(pc):
                if pc.provider_type == ProviderType.OPENAI:
                    return fail_provider
                return success_provider

            mock_factory.create.side_effect = create_provider
            async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                pass

        summary = service.get_metrics_summary()
        assert summary["total_requests"] == 2
        assert summary["successful"] == 1
        assert summary["failed"] == 1

    @pytest.mark.asyncio
    async def test_streaming_with_user_id(self):
        service = UniversalAIService(config=_openai_config())
        provider = _make_streaming_provider(["user", " ", "stream"])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream(
                [{"role": "user", "content": "Hi"}], user_id="user-1"
            ):
                tokens.append(token)

        assert tokens == ["user", " ", "stream"]

    @pytest.mark.asyncio
    async def test_streaming_no_tokens_yields_empty(self):
        service = UniversalAIService(config=_openai_config())
        provider = _make_streaming_provider([])

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream([{"role": "user", "content": "Hi"}]):
                tokens.append(token)

        assert tokens == []
        history = service.get_metrics_history()
        assert len(history) == 1
        assert history[0].success is True
