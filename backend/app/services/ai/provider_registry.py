"""Provider registry — discovery, selection, and fallback chain management."""
import logging
import os
from typing import Any, Dict, List, Optional

from app.services.ai.error_classifier import ConfigurationError
from app.services.ai.types import ProviderConfig, ProviderType

logger = logging.getLogger(__name__)


def _load_config() -> ProviderConfig:
    """Load provider configuration from environment variables.

    Raises:
        ConfigurationError: If AI_PROVIDER is missing, invalid, or required credentials are missing.

    Returns:
        ProviderConfig with validated configuration.
    """
    provider_str = os.getenv("AI_PROVIDER", "").strip().lower()

    if not provider_str:
        raise ConfigurationError(
            "AI_PROVIDER environment variable is required. "
            "Set it to one of: gemini, openai, anthropic. "
            "Example: AI_PROVIDER=openai"
        )

    type_map = {
        "gemini": ProviderType.GEMINI,
        "openai": ProviderType.OPENAI,
        "anthropic": ProviderType.ANTHROPIC,
        "claude": ProviderType.ANTHROPIC,
    }
    provider_type = type_map.get(provider_str)

    if provider_type is None:
        valid_providers = ", ".join(sorted(type_map.keys()))
        raise ConfigurationError(
            f"Invalid AI_PROVIDER value: '{provider_str}'. "
            f"Must be one of: {valid_providers}"
        )

    temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("AI_MAX_TOKENS", "8192"))
    timeout = float(os.getenv("AI_TIMEOUT", "60.0"))
    max_retries = int(os.getenv("AI_MAX_RETRIES", "3"))
    retry_base_delay = float(os.getenv("AI_RETRY_BASE_DELAY", "1.0"))
    retry_max_delay = float(os.getenv("AI_RETRY_MAX_DELAY", "30.0"))

    if provider_type == ProviderType.GEMINI:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY is required when AI_PROVIDER=gemini. "
                "Get your key from https://makersuite.google.com/app/apikey"
            )
        return ProviderConfig(
            provider_type=ProviderType.GEMINI,
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
        )

    if provider_type == ProviderType.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is required when AI_PROVIDER=openai. "
                "For OpenRouter: use your OpenRouter API key."
            )
        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        model = os.getenv("OPENAI_MODEL", "").strip()
        if not model:
            raise ConfigurationError(
                "OPENAI_MODEL is required when AI_PROVIDER=openai. "
                "Examples: openai/gpt-4.1-mini (OpenRouter), gpt-4o-mini (OpenAI)"
            )
        return ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
            base_url=base_url,
        )

    if provider_type == ProviderType.ANTHROPIC:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic. "
                "Get your key from https://console.anthropic.com/"
            )
        return ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key=api_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            retry_base_delay=retry_base_delay,
            retry_max_delay=retry_max_delay,
        )

    raise ConfigurationError(f"Unhandled provider type: {provider_type}")


def validate_provider_config() -> ProviderConfig:
    """Validate AI provider configuration and return the config."""
    return _load_config()


def log_provider_info(config: Optional[ProviderConfig] = None, fallback_chain: Optional[List[ProviderType]] = None) -> None:
    """Log AI provider configuration at startup."""
    if config is None:
        try:
            config = _load_config()
        except ConfigurationError as e:
            logger.error("AI Provider Configuration Error: %s", e)
            raise

    provider_display_names = {
        ProviderType.GEMINI: "Google Gemini",
        ProviderType.OPENAI: "OpenAI Compatible",
        ProviderType.ANTHROPIC: "Anthropic Claude",
    }

    provider_name = provider_display_names.get(config.provider_type, config.provider_type.value)
    api_type = "OpenAI Compatible" if config.provider_type == ProviderType.OPENAI else provider_name

    logger.info("=" * 60)
    logger.info("AI Provider Configuration")
    logger.info("=" * 60)
    logger.info("  AI Provider : %s", provider_name)
    logger.info("  Provider API: %s", api_type)
    logger.info("  Model       : %s", config.model)
    if config.base_url:
        logger.info("  Base URL    : %s", config.base_url)
    if fallback_chain:
        chain_names = [pt.value for pt in fallback_chain]
        logger.info("  Fallback    : %s", " → ".join(chain_names))
    else:
        logger.info("  Fallback    : none")
    logger.info("=" * 60)


class ProviderRegistry:
    """Manages provider configurations, selection, and fallback chain."""

    def __init__(self):
        self._providers: Dict[ProviderType, ProviderConfig] = {}
        self._fallback_chain: List[ProviderType] = []

    def register(self, provider_type: ProviderType, config: ProviderConfig) -> None:
        self._providers[provider_type] = config

    def select(self, preferred: Optional[ProviderType] = None) -> Optional[ProviderConfig]:
        if preferred and preferred in self._providers:
            config = self._providers[preferred]
            if config.enabled:
                return config
        enabled = [c for c in self._providers.values() if c.enabled]
        if not enabled:
            return None
        enabled.sort(key=lambda c: c.priority)
        return enabled[0]

    def get_fallback_chain(self) -> List[ProviderConfig]:
        if self._fallback_chain:
            return [self._providers[pt] for pt in self._fallback_chain if pt in self._providers]
        enabled = [c for c in self._providers.values() if c.enabled]
        enabled.sort(key=lambda c: c.priority)
        return enabled

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "provider_type": c.provider_type.value,
                "model": c.model,
                "enabled": c.enabled,
                "priority": c.priority,
            }
            for c in sorted(self._providers.values(), key=lambda c: c.priority)
        ]

    def load_from_env(self) -> None:
        """Load provider configurations from environment variables."""
        try:
            config = _load_config()
            self.register(config.provider_type, config)
        except ConfigurationError:
            pass

        fallback_str = os.getenv("AI_FALLBACK_CHAIN", "").strip()
        if fallback_str:
            type_map = {
                "gemini": ProviderType.GEMINI,
                "openai": ProviderType.OPENAI,
                "anthropic": ProviderType.ANTHROPIC,
                "claude": ProviderType.ANTHROPIC,
            }
            chain = []
            for name in fallback_str.split(","):
                name = name.strip().lower()
                if name in type_map:
                    chain.append(type_map[name])
                elif name:
                    raise ConfigurationError(f"Invalid provider in AI_FALLBACK_CHAIN: '{name}'")
            self._fallback_chain = chain
