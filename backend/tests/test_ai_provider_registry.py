"""Tests for ProviderRegistry and config loading."""
import pytest
from app.services.ai.error_classifier import ConfigurationError
from app.services.ai.provider_registry import ProviderRegistry, _load_config, log_provider_info
from app.services.ai.types import ProviderConfig, ProviderType


class TestLoadConfig:
    def test_load_gemini(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.GEMINI

    def test_load_openai(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
        config = _load_config()
        assert config.provider_type == ProviderType.OPENAI

    def test_load_anthropic(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.ANTHROPIC

    def test_claude_alias(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "claude")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        config = _load_config()
        assert config.provider_type == ProviderType.ANTHROPIC

    def test_missing_provider_raises(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        with pytest.raises(ConfigurationError, match="AI_PROVIDER environment variable is required"):
            _load_config()

    def test_invalid_provider_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "invalid-provider")
        with pytest.raises(ConfigurationError, match="Invalid AI_PROVIDER value"):
            _load_config()

    def test_gemini_missing_key_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "gemini")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is required"):
            _load_config()

    def test_openai_missing_key_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY is required"):
            _load_config()

    def test_openai_missing_model_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        with pytest.raises(ConfigurationError, match="OPENAI_MODEL is required"):
            _load_config()

    def test_env_overrides(self, monkeypatch):
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


class TestProviderRegistry:
    def test_register_and_select(self):
        reg = ProviderRegistry()
        config = ProviderConfig(provider_type=ProviderType.GEMINI, api_key="key", priority=0)
        reg.register(ProviderType.GEMINI, config)
        selected = reg.select()
        assert selected is not None
        assert selected.provider_type == ProviderType.GEMINI

    def test_select_preferred(self):
        reg = ProviderRegistry()
        reg.register(ProviderType.GEMINI, ProviderConfig(provider_type=ProviderType.GEMINI, api_key="k1", priority=0))
        reg.register(ProviderType.OPENAI, ProviderConfig(provider_type=ProviderType.OPENAI, api_key="k2", priority=1))
        selected = reg.select(ProviderType.OPENAI)
        assert selected.provider_type == ProviderType.OPENAI

    def test_disabled_provider_skipped(self):
        reg = ProviderRegistry()
        reg.register(ProviderType.GEMINI, ProviderConfig(provider_type=ProviderType.GEMINI, enabled=False))
        reg.register(ProviderType.OPENAI, ProviderConfig(provider_type=ProviderType.OPENAI, api_key="k"))
        selected = reg.select()
        assert selected.provider_type == ProviderType.OPENAI

    def test_fallback_chain_ordering(self):
        reg = ProviderRegistry()
        reg.register(ProviderType.OPENAI, ProviderConfig(provider_type=ProviderType.OPENAI, priority=0))
        reg.register(ProviderType.GEMINI, ProviderConfig(provider_type=ProviderType.GEMINI, priority=1))
        reg.register(ProviderType.ANTHROPIC, ProviderConfig(provider_type=ProviderType.ANTHROPIC, priority=2))
        chain = reg.get_fallback_chain()
        assert [c.provider_type for c in chain] == [ProviderType.OPENAI, ProviderType.GEMINI, ProviderType.ANTHROPIC]

    def test_list_providers(self):
        reg = ProviderRegistry()
        reg.register(ProviderType.GEMINI, ProviderConfig(provider_type=ProviderType.GEMINI, model="gemini-2.0-flash"))
        providers = reg.list_providers()
        assert len(providers) == 1
        assert providers[0]["provider_type"] == "gemini"

    def test_load_from_env(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "gemini,anthropic")
        reg = ProviderRegistry()
        reg.load_from_env()
        assert ProviderType.OPENAI in reg._providers
        assert reg._fallback_chain == [ProviderType.GEMINI, ProviderType.ANTHROPIC]

    def test_invalid_fallback_chain_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "invalid-provider")
        reg = ProviderRegistry()
        with pytest.raises(ConfigurationError, match="Invalid provider in AI_FALLBACK_CHAIN"):
            reg.load_from_env()


class TestTask2_2FallbackConfiguration:
    """Task 2.2: Fallback configuration tests."""

    def test_log_provider_info_with_fallback_chain(self, caplog):
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="key",
            model="gpt-4o-mini",
        )
        chain = [ProviderType.GEMINI, ProviderType.ANTHROPIC]
        with caplog.at_level("INFO", logger="app.services.ai.provider_registry"):
            log_provider_info(config=config, fallback_chain=chain)
        assert "Fallback    : gemini → anthropic" in caplog.text

    def test_log_provider_info_without_fallback_chain(self, caplog):
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="key",
            model="gpt-4o-mini",
        )
        with caplog.at_level("INFO", logger="app.services.ai.provider_registry"):
            log_provider_info(config=config)
        assert "Fallback    : none" in caplog.text

    def test_log_provider_info_with_empty_fallback_chain(self, caplog):
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="key",
            model="gpt-4o-mini",
        )
        with caplog.at_level("INFO", logger="app.services.ai.provider_registry"):
            log_provider_info(config=config, fallback_chain=[])
        assert "Fallback    : none" in caplog.text

    def test_load_from_env_with_fallback_chain(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "gemini,anthropic")
        reg = ProviderRegistry()
        reg.load_from_env()
        assert reg._fallback_chain == [ProviderType.GEMINI, ProviderType.ANTHROPIC]

    def test_load_from_env_without_fallback_chain(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.delenv("AI_FALLBACK_CHAIN", raising=False)
        reg = ProviderRegistry()
        reg.load_from_env()
        assert reg._fallback_chain == []

    def test_load_from_env_empty_fallback_chain(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "")
        reg = ProviderRegistry()
        reg.load_from_env()
        assert reg._fallback_chain == []

    def test_load_from_env_whitespace_fallback_chain(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "  gemini , anthropic  ")
        reg = ProviderRegistry()
        reg.load_from_env()
        assert reg._fallback_chain == [ProviderType.GEMINI, ProviderType.ANTHROPIC]

    def test_load_from_env_claude_alias_in_fallback(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "claude")
        reg = ProviderRegistry()
        reg.load_from_env()
        assert reg._fallback_chain == [ProviderType.ANTHROPIC]

    def test_load_from_env_invalid_name_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "key")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("AI_FALLBACK_CHAIN", "ollama")
        reg = ProviderRegistry()
        with pytest.raises(ConfigurationError, match="Invalid provider in AI_FALLBACK_CHAIN"):
            reg.load_from_env()

    def test_get_fallback_chain_respects_explicit_chain(self):
        reg = ProviderRegistry()
        reg.register(ProviderType.OPENAI, ProviderConfig(provider_type=ProviderType.OPENAI, priority=0))
        reg.register(ProviderType.GEMINI, ProviderConfig(provider_type=ProviderType.GEMINI, priority=1))
        reg.register(ProviderType.ANTHROPIC, ProviderConfig(provider_type=ProviderType.ANTHROPIC, priority=2))
        # Set explicit chain (reversed from priority order)
        reg._fallback_chain = [ProviderType.ANTHROPIC, ProviderType.GEMINI, ProviderType.OPENAI]
        chain = reg.get_fallback_chain()
        assert [c.provider_type for c in chain] == [ProviderType.ANTHROPIC, ProviderType.GEMINI, ProviderType.OPENAI]
