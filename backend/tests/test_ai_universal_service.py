"""Integration tests for the rewritten UniversalAIService orchestrator."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.universal_service import UniversalAIService, get_ai_service, reset_ai_service
from app.services.ai.error_classifier import AuthenticationError, ProviderUnavailableError
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


class TestUniversalAIServiceOrchestrator:
    @pytest.mark.asyncio
    async def test_generate_openai(self):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages)
            assert response.content == "Hello"
            assert response.provider == ProviderType.OPENAI

    @pytest.mark.asyncio
    async def test_generate_with_user_id(self):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages, user_id="user-123")
            assert response.content == "Hello"

    @pytest.mark.asyncio
    async def test_generate_without_user_id_skips_budget(self):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages)
            assert response.content == "Hello"

    @pytest.mark.asyncio
    async def test_metrics_recorded(self):
        service = UniversalAIService(config=_openai_config())
        mock_response = _mock_openai_response()
        with patch.dict("sys.modules", {"openai": _mock_openai_sdk(mock_response)}):
            await service.generate([{"role": "user", "content": "test"}])
            history = service.get_metrics_history()
            assert len(history) == 1
            assert history[0].success is True
            assert history[0].total_tokens > 0

    @pytest.mark.asyncio
    async def test_metrics_summary(self):
        service = UniversalAIService(config=_openai_config())
        summary = service.get_metrics_summary()
        assert summary["total_requests"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self):
        service = UniversalAIService(config=_openai_config())
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_client.models.list.return_value = []
        mock_openai.OpenAI.return_value = mock_client
        with patch.dict("sys.modules", {"openai": mock_openai}):
            assert await service.health_check() is True

    def test_parse_json_response(self):
        service = UniversalAIService(config=_openai_config())
        import json
        data = {"key": "value"}
        assert service.parse_json_response(json.dumps(data)) == data

    def test_singleton(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        reset_ai_service()
        s1 = get_ai_service()
        s2 = get_ai_service()
        assert s1 is s2
        reset_ai_service()

    @pytest.mark.asyncio
    async def test_auth_error_not_retried(self):
        service = UniversalAIService(config=_openai_config(max_retries=3))
        provider = MagicMock()
        provider.generate = AsyncMock(side_effect=AuthenticationError("Invalid key"))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = provider
            with pytest.raises(ProviderUnavailableError) as exc_info:
                await service.generate([{"role": "user", "content": "Hello"}])
            assert "Invalid key" in str(exc_info.value)
            assert provider.generate.call_count == 1

    @pytest.mark.asyncio
    async def test_retryable_error_retries(self):
        service = UniversalAIService(config=_openai_config(max_retries=2, retry_base_delay=0.01, retry_max_delay=0.1))
        mock_response = _mock_openai_response()
        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=[
            Exception("503 Service unavailable"),
            mock_response,
        ])
        mock_openai.AsyncOpenAI.return_value = mock_client
        with patch.dict("sys.modules", {"openai": mock_openai}):
            response = await service.generate([{"role": "user", "content": "Hello"}])
            assert response.content == "Hello"
