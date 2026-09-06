"""OpenAI provider implementation."""
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.services.ai.error_classifier import (
    AuthenticationError,
    ProviderUnavailableError,
)
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI provider using openai SDK (AsyncOpenAI)."""

    provider_type = ProviderType.OPENAI

    def __init__(self, config: ProviderConfig):
        self.config = config

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> ProviderResponse:
        if not self.config.api_key:
            raise AuthenticationError("OPENAI_API_KEY not set", provider=ProviderType.OPENAI)

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ProviderUnavailableError("openai package not installed. pip install openai", provider=ProviderType.OPENAI)

        client_kwargs: Dict[str, Any] = {"api_key": self.config.api_key, "timeout": self.config.timeout}
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url

        client = AsyncOpenAI(**client_kwargs)

        start = time.time()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=self.config.top_p,
        )
        latency_ms = (time.time() - start) * 1000

        choice = response.choices[0]
        return ProviderResponse(
            content=choice.message.content or "",
            model=response.model,
            provider=ProviderType.OPENAI,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason or "",
            raw_response=response,
            latency_ms=latency_ms,
        )

    async def health_check(self, api_key: str, model: str) -> bool:
        if not api_key:
            return False
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=10)
            client.models.list()
            return True
        except Exception as e:
            logger.debug("OpenAI health check failed: %s", e)
            return False

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        # Streaming not implemented in Phase 1 — falls back to generate
        response = await self.generate(messages, model, temperature, max_tokens, **kwargs)
        yield response.content
