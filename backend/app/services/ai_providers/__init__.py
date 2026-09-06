"""AI Provider abstraction package.

Re-exports the public interface from the decomposed ai/ package.
"""
from app.services.ai_service import (
    ProviderConfig,
    ProviderMetrics,
    ProviderResponse,
    ProviderType,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ProviderUnavailableError,
    InvalidResponseError,
    ResponseParsingError,
    estimate_cost,
    UniversalAIService,
    get_ai_service,
    reset_ai_service,
)

__all__ = [
    "ProviderConfig",
    "ProviderMetrics",
    "ProviderResponse",
    "ProviderType",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "ProviderUnavailableError",
    "InvalidResponseError",
    "ResponseParsingError",
    "estimate_cost",
    "UniversalAIService",
    "get_ai_service",
    "reset_ai_service",
]
