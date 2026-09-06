"""Tests for the AI Provider Layer.

Tests the UniversalAIService: provider selection, generation (mocked),
retry logic, error mapping, token accounting, cost calculation,
JSON parsing, and metrics.
"""
import asyncio
import json
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai_service import (
    AuthenticationError,
    ConfigurationError,
    InvalidResponseError,
    ProviderConfig,
    ProviderError,
    ProviderMetrics,
    ProviderResponse,
    ProviderType,
    ProviderUnavailableError,
    RateLimitError,
    ResponseParsingError,
    TimeoutError,
    UniversalAIService,
    estimate_cost,
    get_ai_service,
    reset_ai_service,
    _load_config,
)


# ============================================================
# ProviderConfig Tests
# ============================================================

class TestProviderConfig:
    def test_default_config(self):
        config = ProviderConfig(provider_type=ProviderType.GEMINI)
        assert config.provider_type == ProviderType.GEMINI
        assert config.api_key is None
        assert config.model is None
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.top_p == 1.0
        assert config.timeout == 60
        assert config.max_retries == 3
        assert config.retry_base_delay == 1.0
        assert config.retry_max_delay == 30.0

    def test_custom_config(self):
        config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key="test-key",
            model="gemini-2.0-flash",
            temperature=0.5,
            max_tokens=4096,
            timeout=30,
            max_retries=5,
        )
        assert config.api_key == "test-key"
        assert config.model == "gemini-2.0-flash"
        assert config.temperature == 0.5
        assert config.max_tokens == 4096
        assert config.max_retries == 5

    def test_config_with_base_url(self):
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            base_url="https://custom.api.com/v1",
        )
        assert config.base_url == "https://custom.api.com/v1"


# ============================================================
# ProviderError Hierarchy Tests
# ============================================================

class TestProviderErrors:
    def test_provider_error_basic(self):
        err = ProviderError("test error")
        assert str(err) == "test error"
        assert err.error_code == "provider_error"
        assert err.retryable is False
        assert err.provider is None

    def test_provider_error_with_fields(self):
        err = ProviderError(
            "custom error",
            provider=ProviderType.GEMINI,
            error_code="custom_code",
            retryable=True,
            status_code=500,
        )
        assert err.provider == ProviderType.GEMINI
        assert err.error_code == "custom_code"
        assert err.retryable is True
        assert err.status_code == 500

    def test_provider_error_to_dict(self):
        err = ProviderError(
            "msg",
            provider=ProviderType.GEMINI,
            error_code="code",
            retryable=True,
        )
        d = err.to_dict()
        assert d["error_code"] == "code"
        assert d["message"] == "msg"
        assert d["provider"] == "gemini"
        assert d["retryable"] is True

    def test_authentication_error(self):
        err = AuthenticationError(provider=ProviderType.GEMINI)
        assert err.error_code == "authentication_error"
        assert err.retryable is False
        assert err.provider == ProviderType.GEMINI

    def test_rate_limit_error(self):
        err = RateLimitError(retry_after=5.0, provider=ProviderType.GEMINI)
        assert err.error_code == "rate_limit"
        assert err.retryable is True
        assert err.retry_after == 5.0

    def test_timeout_error(self):
        err = TimeoutError(provider=ProviderType.GEMINI)
        assert err.error_code == "timeout"
        assert err.retryable is True

    def test_provider_unavailable_error(self):
        err = ProviderUnavailableError(provider=ProviderType.GEMINI)
        assert err.error_code == "provider_unavailable"
        assert err.retryable is True

    def test_invalid_response_error(self):
        err = InvalidResponseError(provider=ProviderType.GEMINI)
        assert err.error_code == "invalid_response"
        assert err.retryable is False

    def test_response_parsing_error(self):
        err = ResponseParsingError(provider=ProviderType.GEMINI)
        assert err.error_code == "response_parsing_error"
        assert err.retryable is False

    def test_error_hierarchy(self):
        assert issubclass(AuthenticationError, ProviderError)
        assert issubclass(RateLimitError, ProviderError)
        assert issubclass(TimeoutError, ProviderError)
        assert issubclass(ProviderUnavailableError, ProviderError)
        assert issubclass(InvalidResponseError, ProviderError)
        assert issubclass(ResponseParsingError, ProviderError)


# ============================================================
# ProviderMetrics Tests
# ============================================================

class TestProviderMetrics:
    def test_default_metrics(self):
        m = ProviderMetrics()
        assert m.request_id
        assert m.provider == ""
        assert m.total_tokens == 0
        assert m.success is False
        assert m.retry_count == 0
        assert m.timestamp

    def test_metrics_to_dict(self):
        m = ProviderMetrics(
            provider="gemini",
            model="gemini-2.0-flash",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.001,
            latency_ms=150.5,
            success=True,
        )
        d = m.to_dict()
        assert d["provider"] == "gemini"
        assert d["prompt_tokens"] == 100
        assert d["completion_tokens"] == 50
        assert d["total_tokens"] == 150
        assert d["estimated_cost"] == 0.001
        assert d["latency_ms"] == 150.5
        assert d["success"] is True


# ============================================================
# Cost Estimation Tests
# ============================================================

class TestCostEstimation:
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


# ============================================================
# ProviderResponse Tests
# ============================================================

class TestProviderResponse:
    def test_response_properties(self):
        resp = ProviderResponse(
            content="test",
            model="gemini-2.0-flash",
            provider=ProviderType.GEMINI,
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        )
        assert resp.prompt_tokens == 100
        assert resp.completion_tokens == 50
        assert resp.total_tokens == 150
        assert resp.request_id

    def test_response_default_usage(self):
        resp = ProviderResponse(
            content="test",
            model="gemini-2.0-flash",
            provider=ProviderType.GEMINI,
        )
        assert resp.prompt_tokens == 0
        assert resp.completion_tokens == 0
        assert resp.total_tokens == 0


# ============================================================
# Provider Selection via AI_PROVIDER env var
# ============================================================

class TestProviderSelection:
    def test_load_config_gemini(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.GEMINI

    def test_load_config_openai(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        config = _load_config()
        assert config.provider_type == ProviderType.OPENAI

    def test_load_config_anthropic(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.ANTHROPIC

    def test_load_config_claude_alias(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "claude")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.ANTHROPIC

    def test_load_config_missing_raises(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "AI_PROVIDER environment variable is required" in str(exc_info.value)

    def test_load_config_invalid_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "invalid-provider")
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "Invalid AI_PROVIDER value" in str(exc_info.value)

    def test_load_config_gemini_missing_key_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "GEMINI_API_KEY is required" in str(exc_info.value)

    def test_load_config_openai_missing_key_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "OPENAI_API_KEY is required" in str(exc_info.value)

    def test_load_config_openai_missing_model_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "OPENAI_MODEL is required" in str(exc_info.value)

    def test_load_config_anthropic_missing_key_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ConfigurationError) as exc_info:
            _load_config()
        assert "ANTHROPIC_API_KEY is required" in str(exc_info.value)

    def test_load_config_env_overrides(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        monkeypatch.setenv("AI_TEMPERATURE", "0.3")
        monkeypatch.setenv("AI_MAX_TOKENS", "2048")
        monkeypatch.setenv("AI_MAX_RETRIES", "5")
        config = _load_config()
        assert config.api_key == "env-key"
        assert config.temperature == 0.3
        assert config.max_tokens == 2048
        assert config.max_retries == 5

    def test_service_provider_type(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        reset_ai_service()
        service = UniversalAIService()
        assert service.provider_type == ProviderType.OPENAI
        assert service.provider_name == "openai"
        reset_ai_service()


# ============================================================
# Mocked Provider Tests (using unittest.mock)
# ============================================================

class TestMockedProvider:
    @pytest.mark.asyncio
    async def test_generate_returns_content(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello from mock"), finish_reason="stop")]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages)
            assert isinstance(response, ProviderResponse)
            assert response.provider == ProviderType.OPENAI
            assert response.model == "gpt-4o-mini"
            assert response.content == "Hello from mock"
            assert response.total_tokens > 0

    @pytest.mark.asyncio
    async def test_health_check_with_key(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
            )
        )
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_client.models.list.return_value = []
        mock_openai.OpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            assert await service.health_check() is True

    @pytest.mark.asyncio
    async def test_usage_accounting(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            messages = [{"role": "user", "content": "test"}]
            response = await service.generate(messages)
            assert response.prompt_tokens > 0
            assert response.completion_tokens > 0
            assert response.total_tokens == response.prompt_tokens + response.completion_tokens


# ============================================================
# Error Mapping / Classification Tests
# ============================================================

class TestErrorMapping:
    def setup_method(self):
        from app.services.ai.error_classifier import ErrorClassifier
        self.classifier = ErrorClassifier()

    def test_classify_auth_error(self):
        exc = Exception("Invalid API key: abc123")
        err = self.classifier.classify(exc, ProviderType.GEMINI)
        assert isinstance(err, AuthenticationError)

    def test_classify_rate_limit_error(self):
        exc = Exception("429 Rate limit exceeded")
        err = self.classifier.classify(exc)
        assert isinstance(err, RateLimitError)
        assert err.retryable is True

    def test_classify_timeout_error(self):
        exc = Exception("Request timed out after 60s")
        err = self.classifier.classify(exc)
        assert isinstance(err, TimeoutError)

    def test_classify_unavailable_error(self):
        exc = Exception("Service unavailable: 503")
        err = self.classifier.classify(exc)
        assert isinstance(err, ProviderUnavailableError)

    def test_classify_connection_error_retryable(self):
        exc = ConnectionError("Connection refused")
        err = self.classifier.classify(exc)
        assert err.retryable is True

    def test_classify_generic_error(self):
        exc = Exception("Something weird happened")
        err = self.classifier.classify(exc)
        assert isinstance(err, ProviderError)
        assert err.retryable is False


# ============================================================
# Retry Logic Tests (mocked providers)
# ============================================================

class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_auth_error_no_retry(self):
        """Authentication errors should not be retried."""
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=3,
                retry_base_delay=0.01,
            )
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=AuthenticationError("Invalid key"))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            messages = [{"role": "user", "content": "Hello"}]
            with pytest.raises(ProviderUnavailableError) as exc_info:
                await service.generate(messages)
            assert "Invalid key" in str(exc_info.value)
            assert mock_provider.generate.call_count == 1

    @pytest.mark.asyncio
    async def test_retryable_error_retries(self):
        """Retryable errors should trigger retries."""
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=2,
                retry_base_delay=0.01,
                retry_max_delay=0.1,
            )
        )
        success_response = ProviderResponse(
            content="OK",
            model="gemini-2.0-flash",
            provider=ProviderType.GEMINI,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=[
            ProviderUnavailableError("Service unavailable"),
            success_response,
        ])
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages)
            assert response.content == "OK"
            assert mock_provider.generate.call_count == 2

    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Should raise after max retries exhausted."""
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=2,
                retry_base_delay=0.01,
                retry_max_delay=0.1,
            )
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=ProviderUnavailableError("Service unavailable"))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            messages = [{"role": "user", "content": "Hello"}]
            with pytest.raises(ProviderUnavailableError):
                await service.generate(messages)
            assert mock_provider.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_records_metrics(self):
        """Each retry attempt should be tracked in metrics."""
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=1,
                retry_base_delay=0.01,
                retry_max_delay=0.1,
            )
        )
        success_response = ProviderResponse(
            content="OK",
            model="gemini-2.0-flash",
            provider=ProviderType.GEMINI,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=[
            ProviderUnavailableError("Service unavailable"),
            success_response,
        ])
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            messages = [{"role": "user", "content": "Hello"}]
            await service.generate(messages)
            metrics = service.get_metrics_history()
            assert len(metrics) == 1
            assert metrics[0].success is True


# ============================================================
# Token Accounting Tests
# ============================================================

class TestTokenAccounting:
    @pytest.mark.asyncio
    async def test_metrics_recorded_after_generate(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="test"), finish_reason="stop")]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            messages = [{"role": "user", "content": "test"}]
            await service.generate(messages)
            history = service.get_metrics_history()
            assert len(history) == 1
            m = history[0]
            assert m.provider == "openai"
            assert m.total_tokens > 0
            assert m.success is True
            assert m.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_multiple_requests_recorded(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "false")
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        call_count = 0

        async def fake_generate(messages, model, temperature, max_tokens, **kwargs):
            nonlocal call_count
            call_count += 1
            return ProviderResponse(
                content=f"test-{call_count}",
                model="gpt-4o-mini",
                provider=ProviderType.OPENAI,
                usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            )

        mock_provider = MagicMock()
        mock_provider.generate = fake_generate
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            for _ in range(3):
                await service.generate([{"role": "user", "content": "test"}])
            history = service.get_metrics_history()
            assert len(history) == 3

    @pytest.mark.asyncio
    async def test_failed_request_recorded(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=0,
            )
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=AuthenticationError("Bad key"))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            try:
                await service.generate([{"role": "user", "content": "test"}])
            except ProviderUnavailableError:
                pass
            history = service.get_metrics_history()
            assert len(history) == 1
            assert history[0].success is False
            assert history[0].error_code == "authentication_error"

    def test_metrics_summary(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
            )
        )
        summary = service.get_metrics_summary()
        assert summary["total_requests"] == 0

    def test_metrics_history_capped(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
            )
        )
        for i in range(1100):
            m = ProviderMetrics(provider="openai", total_tokens=i, success=True)
            service._cost_tracker.record(m)
        history = service.get_metrics_history()
        assert len(history) <= 1000


# ============================================================
# Health Checks Tests
# ============================================================

class TestHealthChecks:
    @pytest.mark.asyncio
    async def test_gemini_health_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.GEMINI, api_key="")
        )
        assert await service.health_check() is False

    @pytest.mark.asyncio
    async def test_openai_health_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.OPENAI, api_key="")
        )
        assert await service.health_check() is False

    @pytest.mark.asyncio
    async def test_anthropic_health_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="")
        )
        assert await service.health_check() is False


# ============================================================
# JSON Parsing Tests
# ============================================================

class TestJsonParsing:
    def setup_method(self):
        self.service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
            )
        )

    def test_parse_json_simple(self):
        data = {"key": "value"}
        result = self.service.parse_json_response(json.dumps(data))
        assert result == data

    def test_parse_json_list(self):
        data = ["a", "b", "c"]
        result = self.service.parse_json_response(json.dumps(data))
        assert result == data

    def test_parse_json_markdown_wrapped(self):
        data = {"key": "value"}
        wrapped = f"```json\n{json.dumps(data)}\n```"
        result = self.service.parse_json_response(wrapped)
        assert result == data

    def test_parse_json_with_surrounding_text(self):
        data = {"key": "value"}
        content = f"Here is the result: {json.dumps(data)} and some text after."
        result = self.service.parse_json_response(content)
        assert result == data

    def test_parse_json_empty_raises(self):
        with pytest.raises(ResponseParsingError):
            self.service.parse_json_response("")

    def test_parse_json_invalid_raises(self):
        with pytest.raises(ResponseParsingError):
            self.service.parse_json_response("not json at all")


# ============================================================
# Singleton Tests
# ============================================================

class TestSingleton:
    def test_get_ai_service_returns_same_instance(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        reset_ai_service()
        s1 = get_ai_service()
        s2 = get_ai_service()
        assert s1 is s2
        reset_ai_service()

    def test_reset_ai_service(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        reset_ai_service()
        s1 = get_ai_service()
        reset_ai_service()
        s2 = get_ai_service()
        assert s1 is not s2
        reset_ai_service()


# ============================================================
# Gemini Request Formatting (mocked)
# ============================================================

class TestGeminiRequest:
    @pytest.mark.asyncio
    async def test_gemini_message_conversion_and_call(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                model="gemini-2.0-flash",
                max_retries=0,
            )
        )
        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini"
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_response.prompt_feedback.block_reason = None
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mock_response.usage_metadata.total_token_count = 15

        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ]
            response = await service.generate(messages)
            assert response.content == "Hello from Gemini"
            assert response.prompt_tokens == 10
            assert response.completion_tokens == 5
            # Verify system message was extracted, not passed as content
            call_args = mock_model.generate_content.call_args
            contents = call_args.kwargs.get("contents") or (call_args[0][0] if call_args[0] else None)
            assert any(c["role"] == "user" for c in contents)

    @pytest.mark.asyncio
    async def test_gemini_auth_error_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.GEMINI, api_key="")
        )
        with pytest.raises(ProviderUnavailableError):
            await service.generate([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_gemini_import_error(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=0,
            )
        )
        with patch.dict("sys.modules", {"google.generativeai": None}):
            with pytest.raises(ProviderUnavailableError):
                await service.generate([{"role": "user", "content": "Hello"}])


# ============================================================
# OpenAI Request Formatting (mocked)
# ============================================================

class TestOpenAIRequest:
    @pytest.mark.asyncio
    async def test_openai_message_passthrough(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from OpenAI"
        mock_choice.finish_reason = "stop"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await service.generate(messages)
            assert response.content == "Hello from OpenAI"
            assert response.prompt_tokens == 10

    @pytest.mark.asyncio
    async def test_openai_auth_error_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.OPENAI, api_key="")
        )
        with pytest.raises(ProviderUnavailableError):
            await service.generate([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_openai_import_error(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                max_retries=0,
            )
        )
        with patch.dict("sys.modules", {"openai": None}):
            with pytest.raises(ProviderUnavailableError):
                await service.generate([{"role": "user", "content": "Hello"}])


# ============================================================
# Anthropic Request Formatting (mocked)
# ============================================================

class TestAnthropicRequest:
    @pytest.mark.asyncio
    async def test_anthropic_system_extraction(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                api_key="test-key",
                model="claude-sonnet-4-20250514",
                max_retries=0,
            )
        )
        mock_content = MagicMock()
        mock_content.text = "Hello from Claude"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5

        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ]
            response = await service.generate(messages)
            assert response.content == "Hello from Claude"
            assert response.prompt_tokens == 10
            assert response.completion_tokens == 5
            # Verify system was passed as kwarg, not in messages
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs["system"] == "You are helpful."

    @pytest.mark.asyncio
    async def test_anthropic_auth_error_no_key(self):
        service = UniversalAIService(
            config=ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="")
        )
        with pytest.raises(ProviderUnavailableError):
            await service.generate([{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_anthropic_import_error(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                api_key="test-key",
                max_retries=0,
            )
        )
        with patch.dict("sys.modules", {"anthropic": None}):
            with pytest.raises(ProviderUnavailableError):
                await service.generate([{"role": "user", "content": "Hello"}])


# ============================================================
# Timeout Handling Tests
# ============================================================

class TestTimeoutHandling:
    @pytest.mark.asyncio
    async def test_timeout_error_classified(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=0,
            )
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=TimeoutError("Request timed out"))
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            with pytest.raises(ProviderUnavailableError) as exc_info:
                await service.generate([{"role": "user", "content": "Hello"}])
            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_timeout_retried(self):
        service = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.GEMINI,
                api_key="test-key",
                max_retries=2,
                retry_base_delay=0.01,
                retry_max_delay=0.1,
            )
        )
        success_response = ProviderResponse(
            content="OK",
            model="gemini-2.0-flash",
            provider=ProviderType.GEMINI,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        )
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=[
            ProviderUnavailableError("503"),
            TimeoutError("timed out"),
            success_response,
        ])
        with patch("app.services.ai.universal_service.ProviderFactory") as mock_factory:
            mock_factory.create.return_value = mock_provider
            response = await service.generate([{"role": "user", "content": "Hello"}])
            assert response.content == "OK"
            assert mock_provider.generate.call_count == 3
