"""Error hierarchy and classification for AI provider exceptions."""
from typing import Any, Dict, Optional, Type

from app.services.ai.types import ProviderType


class ProviderError(Exception):
    def __init__(
        self,
        message: str,
        provider: Optional[ProviderType] = None,
        error_code: str = "provider_error",
        retryable: bool = False,
        status_code: Optional[int] = None,
        raw_error: Optional[Exception] = None,
    ):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        self.retryable = retryable
        self.status_code = status_code
        self.raw_error = raw_error
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "provider": self.provider.value if self.provider else None,
            "retryable": self.retryable,
            "status_code": self.status_code,
        }


class AuthenticationError(ProviderError):
    def __init__(self, message: str = "Invalid API key", **kwargs):
        super().__init__(message, error_code="authentication_error", retryable=False, **kwargs)


class RateLimitError(ProviderError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None, **kwargs):
        super().__init__(message, error_code="rate_limit", retryable=True, **kwargs)
        self.retry_after = retry_after


class TimeoutError(ProviderError):
    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, error_code="timeout", retryable=True, **kwargs)


class ProviderUnavailableError(ProviderError):
    def __init__(self, message: str = "Provider unavailable", **kwargs):
        super().__init__(message, error_code="provider_unavailable", retryable=True, **kwargs)


class InvalidResponseError(ProviderError):
    def __init__(self, message: str = "Invalid provider response", **kwargs):
        super().__init__(message, error_code="invalid_response", retryable=False, **kwargs)


class ResponseParsingError(ProviderError):
    def __init__(self, message: str = "Failed to parse response", **kwargs):
        super().__init__(message, error_code="response_parsing_error", retryable=False, **kwargs)


class ConfigurationError(ProviderError):
    def __init__(self, message: str = "AI provider configuration error", **kwargs):
        super().__init__(message, error_code="configuration_error", retryable=False, **kwargs)


class TokenBudgetExceeded(ProviderError):
    def __init__(self, message: str = "Token budget exceeded", **kwargs):
        super().__init__(message, error_code="token_budget_exceeded", retryable=False, **kwargs)


# SDK exception mapping tables — keyed by exception type for resilience
_OPENAI_EXCEPTION_MAP: Dict[Type[Exception], Type[ProviderError]] = {}

_GEMINI_EXCEPTION_MAP: Dict[Type[Exception], Type[ProviderError]] = {}

_ANTHROPIC_EXCEPTION_MAP: Dict[Type[Exception], Type[ProviderError]] = {}


def _build_sdk_maps() -> None:
    """Build SDK exception mapping tables. Called once at import time."""
    try:
        import openai
        _OPENAI_EXCEPTION_MAP.update({
            openai.AuthenticationError: AuthenticationError,
            openai.RateLimitError: RateLimitError,
            openai.APITimeoutError: TimeoutError,
            openai.APIConnectionError: ProviderUnavailableError,
        })
    except (ImportError, AttributeError):
        pass

    try:
        import google.api_core.exceptions as gexc
        _GEMINI_EXCEPTION_MAP.update({
            gexc.PermissionDenied: AuthenticationError,
            gexc.ResourceExhausted: RateLimitError,
            gexc.ServiceUnavailable: ProviderUnavailableError,
            gexc.GatewayTimeout: TimeoutError,
        })
    except (ImportError, AttributeError):
        pass

    try:
        import anthropic
        _ANTHROPIC_EXCEPTION_MAP.update({
            anthropic.AuthenticationError: AuthenticationError,
            anthropic.RateLimitError: RateLimitError,
            anthropic.APITimeoutError: TimeoutError,
        })
    except (ImportError, AttributeError):
        pass


_build_sdk_maps()


class ErrorClassifier:
    """Classifies provider SDK exceptions into ProviderError subclasses."""

    _RETRYABLE_TYPES = frozenset({"rate_limit", "timeout", "provider_unavailable"})

    def classify(self, exc: Exception, provider: Optional[ProviderType] = None) -> ProviderError:
        """Classify an exception into a ProviderError subclass.

        Checks exception type first (SDK-version-resilient), then falls back
        to string matching for unknown exceptions.
        """
        if isinstance(exc, ProviderError):
            return exc

        sdk_map = self._get_sdk_map(provider)
        for sdk_exc_type, provider_err_type in sdk_map.items():
            if isinstance(exc, sdk_exc_type):
                return provider_err_type(
                    f"{type(exc).__name__}: {exc}",
                    provider=provider,
                    raw_error=exc,
                )

        error_str = str(exc).lower()

        auth_keywords = ["api_key", "api key", "invalid key", "unauthorized", "401", "permission denied", "authentication"]
        if any(kw in error_str for kw in auth_keywords):
            return AuthenticationError(f"Auth failed: {exc}", provider=provider, raw_error=exc)

        rate_keywords = ["rate limit", "429", "quota exceeded", "resource exhausted", "too many requests"]
        if any(kw in error_str for kw in rate_keywords):
            return RateLimitError(f"Rate limited: {exc}", provider=provider, raw_error=exc)

        timeout_keywords = ["timeout", "timed out", "deadline", "504"]
        if any(kw in error_str for kw in timeout_keywords):
            return TimeoutError(f"Timeout: {exc}", provider=provider, raw_error=exc)

        unavailable_keywords = ["unavailable", "service error", "503", "502", "internal error", "server error"]
        if any(kw in error_str for kw in unavailable_keywords):
            return ProviderUnavailableError(f"Unavailable: {exc}", provider=provider, raw_error=exc)

        is_retryable = type(exc).__name__ in ("ConnectionError", "TimeoutError", "OSError")
        return ProviderError(
            f"Provider error: {exc}",
            provider=provider,
            error_code="provider_error",
            retryable=is_retryable,
            raw_error=exc,
        )

    def is_retryable(self, error: ProviderError) -> bool:
        """Check if a ProviderError is retryable."""
        return error.retryable

    def _get_sdk_map(self, provider: Optional[ProviderType]) -> Dict[Type[Exception], Type[ProviderError]]:
        if provider == ProviderType.OPENAI:
            return _OPENAI_EXCEPTION_MAP
        if provider == ProviderType.GEMINI:
            return _GEMINI_EXCEPTION_MAP
        if provider == ProviderType.ANTHROPIC:
            return _ANTHROPIC_EXCEPTION_MAP
        combined = {}
        combined.update(_OPENAI_EXCEPTION_MAP)
        combined.update(_GEMINI_EXCEPTION_MAP)
        combined.update(_ANTHROPIC_EXCEPTION_MAP)
        return combined
