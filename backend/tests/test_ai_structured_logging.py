"""Tests for structured logging in UniversalAIService (Task 6.1)."""
import logging
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService
from app.services.ai.response_cache import CachedResponse, ResponseCache
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


class TestStructuredLogging:
    @pytest.mark.asyncio
    async def test_completion_log_contains_required_fields(self, caplog):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
                await service.generate([{"role": "user", "content": "Hello"}])

        records = [r for r in caplog.records if "Request completed" in r.message]
        assert len(records) == 1
        msg = records[0].message
        assert "request_id=" in msg
        assert "provider=openai" in msg
        assert "model=gpt-4o-mini" in msg
        assert "prompt_tokens=" in msg
        assert "completion_tokens=" in msg
        assert "total_tokens=" in msg
        assert "cost=" in msg
        assert "latency_ms=" in msg

    @pytest.mark.asyncio
    async def test_cache_hit_logged(self, caplog):
        service = UniversalAIService(config=_openai_config())
        messages = [{"role": "user", "content": "Hello"}]
        cache_key = ResponseCache.make_key(messages, service.model, 0.7, 2048)
        cached = CachedResponse(
            content="cached", model="gpt-4o-mini", provider="openai",
            usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            finish_reason="stop", latency_ms=50.0, request_id="req-cached",
        )
        await service.cache.set(cache_key, cached)

        with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
            await service.generate(messages)

        records = [r for r in caplog.records if "Cache hit" in r.message]
        assert len(records) == 1
        assert "request_id=req-cached" in records[0].message
        assert "provider=openai" in records[0].message

    @pytest.mark.asyncio
    async def test_cache_miss_logged(self, caplog):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
                await service.generate([{"role": "user", "content": "Hello"}])

        records = [r for r in caplog.records if "Cache miss" in r.message]
        assert len(records) == 1
        assert "model=gpt-4o-mini" in records[0].message

    @pytest.mark.asyncio
    async def test_budget_rejection_logged(self, caplog):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("AI_MAX_INPUT_TOKENS", "10")
        service = UniversalAIService(config=_openai_config())

        with caplog.at_level(logging.WARNING, logger="app.services.ai.token_budget"):
            with pytest.raises(Exception):
                await service.generate([{"role": "user", "content": "a" * 100}])

        records = [r for r in caplog.records if "Budget rejection" in r.message]
        assert len(records) == 1
        assert "input tokens" in records[0].message
        monkeypatch.undo()

    @pytest.mark.asyncio
    async def test_budget_user_daily_rejection_logged(self, caplog):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("AI_USER_DAILY_TOKEN_LIMIT", "10")
        service = UniversalAIService(config=_openai_config())

        provider = MagicMock()

        async def mock_gen(messages, model, temperature, max_tokens, **kwargs):
            return MagicMock(
                content="ok", model="gpt-4o-mini", provider=ProviderType.OPENAI,
                usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
                finish_reason="stop", latency_ms=10.0, request_id="req-1",
                prompt_tokens=5, completion_tokens=3, total_tokens=8,
            )

        provider.generate = mock_gen

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            await service.generate([{"role": "user", "content": "Hello"}], user_id="user-1")

        with caplog.at_level(logging.WARNING, logger="app.services.ai.token_budget"):
            with pytest.raises(Exception):
                await service.generate([{"role": "user", "content": "a" * 200}], user_id="user-1")

        records = [r for r in caplog.records if "Budget rejection" in r.message and "daily" in r.message]
        assert len(records) == 1
        assert "user=user-1" in records[0].message
        monkeypatch.undo()

    @pytest.mark.asyncio
    async def test_streaming_start_logged(self, caplog):
        service = UniversalAIService(config=_openai_config())

        async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
            yield "token"

        provider = MagicMock()
        provider.generate_stream = mock_stream

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
                async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                    pass

        records = [r for r in caplog.records if "Stream started" in r.message]
        assert len(records) == 1
        assert "request_id=" in records[0].message
        assert "model=gpt-4o-mini" in records[0].message

    @pytest.mark.asyncio
    async def test_streaming_completion_logged(self, caplog):
        service = UniversalAIService(config=_openai_config())

        async def mock_stream(messages, model, temperature, max_tokens, **kwargs):
            yield "token"

        provider = MagicMock()
        provider.generate_stream = mock_stream

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
                async for _ in service.generate_stream([{"role": "user", "content": "Hi"}]):
                    pass

        records = [r for r in caplog.records if "Stream completed" in r.message]
        assert len(records) == 1
        assert "provider=openai" in records[0].message
        assert "latency_ms=" in records[0].message

    @pytest.mark.asyncio
    async def test_no_api_keys_in_logs(self, caplog):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            with caplog.at_level(logging.DEBUG, logger="app.services.ai"):
                await service.generate([{"role": "user", "content": "Hello"}])

        for record in caplog.records:
            assert "sk-" not in record.message, f"API key leaked in log: {record.message}"
            assert "test-key" not in record.message, f"API key leaked in log: {record.message}"

    @pytest.mark.asyncio
    async def test_no_prompts_in_logs(self, caplog):
        service = UniversalAIService(config=_openai_config())
        secret_prompt = "My secret resume content with personal info"
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            with caplog.at_level(logging.DEBUG, logger="app.services.ai"):
                await service.generate([{"role": "user", "content": secret_prompt}])

        for record in caplog.records:
            assert secret_prompt not in record.message, f"Prompt leaked in log: {record.message}"

    @pytest.mark.asyncio
    async def test_fallback_logging_preserved(self, caplog):
        config = _openai_config()
        service = UniversalAIService(config=config)

        fallback_config = ProviderConfig(
            provider_type=ProviderType.GEMINI, api_key="test-key",
            model="gemini-2.0-flash", max_retries=0,
        )
        service._registry.register(ProviderType.GEMINI, fallback_config)
        service._fallback_chain = service._registry.get_fallback_chain()

        fail_provider = MagicMock()
        fail_provider.generate = AsyncMock(side_effect=Exception("503 unavailable"))

        success_provider = MagicMock()
        success_provider.generate = AsyncMock(return_value=MagicMock(
            content="ok", model="gemini-2.0-flash", provider=ProviderType.GEMINI,
            usage={"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
            finish_reason="stop", latency_ms=10.0, request_id="req-fb",
            prompt_tokens=5, completion_tokens=3, total_tokens=8,
        ))

        def create_provider(pc):
            if pc.provider_type == ProviderType.OPENAI:
                return fail_provider
            return success_provider

        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.side_effect = create_provider
            with caplog.at_level(logging.INFO, logger="app.services.ai.universal_service"):
                await service.generate([{"role": "user", "content": "Hi"}])

        fallback_records = [r for r in caplog.records if "Fallback succeeded" in r.message]
        assert len(fallback_records) == 1
        assert "openai" in fallback_records[0].message
        assert "gemini" in fallback_records[0].message
