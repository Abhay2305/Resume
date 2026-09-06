"""Protocol defining the interface all AI providers must implement."""
from typing import AsyncGenerator, Dict, List, Protocol, runtime_checkable

from app.services.ai.types import ProviderResponse, ProviderType


@runtime_checkable
class AIProvider(Protocol):
    """All AI providers must implement this interface."""

    provider_type: ProviderType

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> ProviderResponse:
        """Send messages to the provider and return a normalized response."""
        ...

    async def health_check(self, api_key: str, model: str) -> bool:
        """Check if the provider is reachable and the API key is valid."""
        ...

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Yield tokens as they are generated."""
        ...
        yield  # Make this a generator
