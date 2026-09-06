"""Response Parser for AI Execution Engine.

Normalizes provider responses into a single internal format.
No provider-specific code outside UniversalAIService.
"""
import json
import logging
from typing import Any, Dict, Optional

from app.services.ai_service import ProviderResponse, ResponseParsingError

logger = logging.getLogger(__name__)


class ResponseParser:
    """Normalizes AI provider responses into a consistent internal format.

    Handles JSON extraction, markdown cleaning, and response validation.
    """

    @staticmethod
    def parse_to_dict(content: str) -> Dict[str, Any]:
        """Parse AI response content into a dictionary.

        Args:
            content: Raw AI response content.

        Returns:
            Parsed dictionary.

        Raises:
            ResponseParsingError: If content cannot be parsed.
        """
        if not content or not content.strip():
            raise ResponseParsingError("Empty response content")

        cleaned = content.strip()

        # Remove markdown code block wrapping
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        # Try direct JSON parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from text
        for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
            import re
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    continue

        raise ResponseParsingError(f"Failed to parse response as JSON: {cleaned[:200]}...")

    @staticmethod
    def parse_to_text(content: str) -> str:
        """Parse AI response content as clean text.

        Args:
            content: Raw AI response content.

        Returns:
            Cleaned text content.
        """
        if not content:
            return ""

        cleaned = content.strip()

        # Remove markdown code block wrapping if present
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
            if cleaned.startswith("json") or cleaned.startswith("text"):
                cleaned = cleaned[4:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        return cleaned

    @staticmethod
    def validate_response(response: ProviderResponse) -> bool:
        """Validate that a provider response is usable.

        Args:
            response: Provider response to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not response.content:
            return False

        if not response.model:
            return False

        if not response.provider:
            return False

        return True

    @staticmethod
    def extract_metadata(response: ProviderResponse) -> Dict[str, Any]:
        """Extract metadata from a provider response.

        Args:
            response: Provider response.

        Returns:
            Dictionary of metadata.
        """
        return {
            "provider": response.provider.value if response.provider else None,
            "model": response.model,
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
            "finish_reason": response.finish_reason,
            "latency_ms": response.latency_ms,
            "request_id": response.request_id,
        }
