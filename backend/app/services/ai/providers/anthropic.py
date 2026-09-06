"""Anthropic (Claude) provider implementation."""
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.services.ai.error_classifier import (
    AuthenticationError,
    ProviderUnavailableError,
)
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic provider using anthropic SDK."""

    provider_type = ProviderType.ANTHROPIC

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
            raise AuthenticationError("ANTHROPIC_API_KEY not set", provider=ProviderType.ANTHROPIC)

        try:
            import anthropic
        except ImportError:
            raise ProviderUnavailableError("anthropic package not installed. pip install anthropic", provider=ProviderType.ANTHROPIC)

        system_prompt = None
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = f"{system_prompt}\n\n{msg['content']}" if system_prompt else msg["content"]
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        if not api_messages:
            api_messages = [{"role": "user", "content": ""}]

        client = anthropic.Anthropic(api_key=self.config.api_key)

        start = time.time()
        call_kwargs: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": api_messages,
            "temperature": temperature,
        }
        if system_prompt:
            call_kwargs["system"] = system_prompt

        response = client.messages.create(**call_kwargs)
        latency_ms = (time.time() - start) * 1000

        content = response.content[0].text if response.content else ""
        usage = {
            "prompt_tokens": getattr(response.usage, "input_tokens", 0) or 0,
            "completion_tokens": getattr(response.usage, "output_tokens", 0) or 0,
            "total_tokens": (getattr(response.usage, "input_tokens", 0) or 0) + (getattr(response.usage, "output_tokens", 0) or 0),
        }

        return ProviderResponse(
            content=content,
            model=response.model,
            provider=ProviderType.ANTHROPIC,
            usage=usage,
            finish_reason=response.stop_reason or "",
            raw_response=response,
            latency_ms=latency_ms,
        )

    async def health_check(self, api_key: str, model: str) -> bool:
        if not api_key:
            return False
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            return True
        except Exception as e:
            logger.debug("Anthropic health check failed: %s", e)
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
