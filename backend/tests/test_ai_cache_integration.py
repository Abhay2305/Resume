"""Integration tests for ResponseCache in UniversalAIService (Task 4.1)."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService
from app.services.ai.response_cache import CachedResponse, ResponseCache
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType


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


def _mock_openai_response(content="Hello", prompt_tokens=10, completion_tokens=5):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=content), finish_reason="stop")]
    mock_response.model = "gpt-4o-mini"
    mock_response.usage.prompt_tokens = prompt_tokens
    mock_response.usage.completion_tokens = completion_tokens
    mock_response.usage.total_tokens = prompt_tokens + completion_tokens
    return mock_response


def _mock_openai_sdk(mock_response):
    mock_openai = MagicMock()
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_openai.AsyncOpenAI.return_value = mock_client
    return mock_openai


class TestCacheIntegration:
    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_response_without_provider_call(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]
        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        cached = CachedResponse(
            content="Cached answer",
            model="gpt-4o-mini",
            provider="openai",
            usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            finish_reason="stop",
            latency_ms=50.0,
            request_id="cached-req-1",
        )
        await service.cache.set(cache_key, cached)

        provider = MagicMock()
        provider.generate = AsyncMock()
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            response = await service.generate(messages)

        assert response.content == "Cached answer"
        assert response.request_id == "cached-req-1"
        provider.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_miss_calls_provider_and_stores_result(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]
        mock_response = _mock_openai_response(content="Fresh answer")
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            response = await service.generate(messages)

        assert response.content == "Fresh answer"
        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        cached = await service.cache.get(cache_key)
        assert cached is not None
        assert cached.content == "Fresh answer"

    @pytest.mark.asyncio
    async def test_cache_failure_degrades_gracefully(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]
        mock_response = _mock_openai_response(content="Provider answer")

        original_get = service.cache.get

        async def failing_get(key):
            raise RuntimeError("Cache corrupted")

        service.cache.get = failing_get

        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            response = await service.generate(messages)

        assert response.content == "Provider answer"

    @pytest.mark.asyncio
    async def test_streaming_skips_cache(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]
        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        cached = CachedResponse(
            content="Should not be used",
            model="gpt-4o-mini",
            provider="openai",
            usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            finish_reason="stop",
            latency_ms=50.0,
            request_id="cached-req-stream",
        )
        await service.cache.set(cache_key, cached)

        provider = MagicMock()

        async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
            yield "stream"
            yield "token"

        provider.generate_stream = mock_stream
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            tokens = []
            async for token in service.generate_stream(messages):
                tokens.append(token)

        assert tokens == ["stream", "token"]

    @pytest.mark.asyncio
    async def test_cache_metrics_recorded_in_summary(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]

        await service.cache.get("nonexistent-key")
        await service.cache.get("another-miss")

        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            await service.generate(messages)

        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        await service.cache.get(cache_key)

        summary = service.get_metrics_summary()
        assert summary["cache_hits"] == 1
        assert summary["cache_misses"] == 3
        assert summary["cache_hit_rate"] == 0.25

    @pytest.mark.asyncio
    async def test_user_aware_cache_keys_are_different(self):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]

        mock_response_1 = _mock_openai_response(content="Response for user-1")
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response_1)}):
            await service.generate(messages, user_id="user-1")

        mock_response_2 = _mock_openai_response(content="Response for user-2")
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response_2)}):
            await service.generate(messages, user_id="user-2")

        key_u1 = ResponseCache.make_key(messages, service.model, 0.7, 2048, user_id="user-1")
        key_u2 = ResponseCache.make_key(messages, service.model, 0.7, 2048, user_id="user-2")
        assert key_u1 != key_u2

        cached_u1 = await service.cache.get(key_u1)
        cached_u2 = await service.cache.get(key_u2)
        assert cached_u1.content == "Response for user-1"
        assert cached_u2.content == "Response for user-2"

    @pytest.mark.asyncio
    async def test_error_response_not_cached(self):
        from app.services.ai.error_classifier import ProviderError

        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]

        provider = MagicMock()
        provider.generate = AsyncMock(side_effect=ProviderError("API error", retryable=False))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            with pytest.raises(Exception):
                await service.generate(messages)

        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        cached = await service.cache.get(cache_key)
        assert cached is None
