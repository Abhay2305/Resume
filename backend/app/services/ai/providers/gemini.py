"""Google Gemini provider implementation."""
import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.services.ai.error_classifier import (
    AuthenticationError,
    InvalidResponseError,
    ProviderUnavailableError,
)
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Gemini provider using google-generativeai SDK."""

    provider_type = ProviderType.GEMINI

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
            raise AuthenticationError("GEMINI_API_KEY not set", provider=ProviderType.GEMINI)

        try:
            import google.generativeai as genai
        except ImportError:
            raise ProviderUnavailableError("google-generativeai not installed", provider=ProviderType.GEMINI)

        genai.configure(api_key=self.config.api_key)

        system_instruction = None
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_instruction = f"{system_instruction}\n\n{content}" if system_instruction else content
            elif role == "user":
                contents.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [content]})

        if not contents:
            contents = [{"role": "user", "parts": [""]}]

        gemini_model = genai.GenerativeModel(
            model,
            system_instruction=system_instruction,
        )

        gen_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": self.config.top_p,
        }
        gen_config = {k: v for k, v in gen_config.items() if v is not None}

        start = time.time()
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: gemini_model.generate_content(contents=contents, generation_config=gen_config),
        )
        latency_ms = (time.time() - start) * 1000

        if response is None:
            raise InvalidResponseError("Gemini returned null", provider=ProviderType.GEMINI)
        if hasattr(response, "prompt_feedback") and hasattr(response.prompt_feedback, "block_reason") and response.prompt_feedback.block_reason:
            raise InvalidResponseError(f"Gemini blocked: {response.prompt_feedback.block_reason}", provider=ProviderType.GEMINI)

        content = response.text or ""
        usage: Dict[str, int] = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(response.usage_metadata, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(response.usage_metadata, "total_token_count", 0) or 0,
            }

        finish_reason = ""
        if hasattr(response, "candidates") and response.candidates:
            finish_reason = str(response.candidates[0].finish_reason) if hasattr(response.candidates[0], "finish_reason") else ""

        return ProviderResponse(
            content=content.strip(),
            model=model,
            provider=ProviderType.GEMINI,
            usage=usage,
            finish_reason=finish_reason,
            raw_response=response,
            latency_ms=latency_ms,
        )

    async def health_check(self, api_key: str, model: str) -> bool:
        if not api_key:
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            return True
        except Exception as e:
            logger.debug("Gemini health check failed: %s", e)
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
