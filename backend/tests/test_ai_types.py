"""Tests for AI type definitions: ProviderConfig, ProviderResponse, ProviderMetrics."""
import pytest
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderMetrics, ProviderType


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
        assert config.base_url is None
        assert config.priority == 0
        assert config.enabled is True
        assert config.extra == {}

    def test_custom_config(self):
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key",
            model="gpt-4o",
            temperature=0.3,
            max_tokens=4096,
            timeout=30,
            max_retries=5,
            retry_base_delay=0.5,
            retry_max_delay=15.0,
            base_url="https://custom.api.com/v1",
            priority=1,
            enabled=False,
        )
        assert config.api_key == "test-key"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.3
        assert config.max_tokens == 4096
        assert config.timeout == 30
        assert config.max_retries == 5
        assert config.retry_base_delay == 0.5
        assert config.retry_max_delay == 15.0
        assert config.base_url == "https://custom.api.com/v1"
        assert config.priority == 1
        assert config.enabled is False

    def test_extra_dict(self):
        config = ProviderConfig(
            provider_type=ProviderType.GEMINI,
            extra={"project_id": "my-project", "location": "us-central1"},
        )
        assert config.extra["project_id"] == "my-project"
        assert config.extra["location"] == "us-central1"

    def test_extra_dict_default_is_empty(self):
        c1 = ProviderConfig(provider_type=ProviderType.GEMINI)
        c2 = ProviderConfig(provider_type=ProviderType.OPENAI)
        assert c1.extra is not c2.extra
        assert c1.extra == {}
        assert c2.extra == {}


class TestProviderResponse:
    def test_response_properties(self):
        resp = ProviderResponse(
            content="Hello",
            model="gpt-4o",
            provider=ProviderType.OPENAI,
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

    def test_response_request_id_is_unique(self):
        r1 = ProviderResponse(content="a", model="m", provider=ProviderType.GEMINI)
        r2 = ProviderResponse(content="b", model="m", provider=ProviderType.GEMINI)
        assert r1.request_id != r2.request_id


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
            provider="openai",
            model="gpt-4o",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.001,
            latency_ms=150.5,
            success=True,
        )
        d = m.to_dict()
        assert d["provider"] == "openai"
        assert d["prompt_tokens"] == 100
        assert d["completion_tokens"] == 50
        assert d["total_tokens"] == 150
        assert d["estimated_cost"] == 0.001
        assert d["latency_ms"] == 150.5
        assert d["success"] is True
