"""Provider factory — creates provider instances from configuration."""
from typing import Dict, Type

from app.services.ai.providers.base import AIProvider
from app.services.ai.providers.gemini import GeminiProvider
from app.services.ai.providers.openai import OpenAIProvider
from app.services.ai.providers.anthropic import AnthropicProvider
from app.services.ai.types import ProviderConfig, ProviderType


_PROVIDER_MAP: Dict[ProviderType, Type[AIProvider]] = {
    ProviderType.GEMINI: GeminiProvider,
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.ANTHROPIC: AnthropicProvider,
}


class ProviderFactory:
    """Creates AIProvider instances based on ProviderConfig."""

    @staticmethod
    def create(config: ProviderConfig) -> AIProvider:
        provider_cls = _PROVIDER_MAP.get(config.provider_type)
        if provider_cls is None:
            raise ValueError(f"Unknown provider type: {config.provider_type}")
        return provider_cls(config)
