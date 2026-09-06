"""Tests for ErrorClassifier and error hierarchy."""
import pytest
from unittest.mock import MagicMock

from app.services.ai.error_classifier import (
    AuthenticationError,
    ConfigurationError,
    ErrorClassifier,
    InvalidResponseError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
    ResponseParsingError,
    TokenBudgetExceeded,
    TimeoutError,
)
from app.services.ai.types import ProviderType


class TestErrorHierarchy:
    def test_all_errors_subclass_provider_error(self):
        for cls in [AuthenticationError, RateLimitError, TimeoutError,
                    ProviderUnavailableError, InvalidResponseError,
                    ResponseParsingError, ConfigurationError, TokenBudgetExceeded]:
            assert issubclass(cls, ProviderError)

    def test_provider_error_to_dict(self):
        err = ProviderError("msg", provider=ProviderType.GEMINI, error_code="code", retryable=True)
        d = err.to_dict()
        assert d["error_code"] == "code"
        assert d["provider"] == "gemini"
        assert d["retryable"] is True

    def test_rate_limit_error_has_retry_after(self):
        err = RateLimitError(retry_after=5.0)
        assert err.retry_after == 5.0
        assert err.retryable is True

    def test_token_budget_exceeded_not_retryable(self):
        err = TokenBudgetExceeded("over budget")
        assert err.retryable is False
        assert err.error_code == "token_budget_exceeded"


class TestErrorClassifier:
    def setup_method(self):
        self.classifier = ErrorClassifier()

    def test_classify_provider_error_passthrough(self):
        original = AuthenticationError("already classified")
        result = self.classifier.classify(original)
        assert result is original

    def test_classify_auth_error_string(self):
        exc = Exception("Invalid API key: abc123")
        err = self.classifier.classify(exc, ProviderType.GEMINI)
        assert isinstance(err, AuthenticationError)
        assert err.provider == ProviderType.GEMINI

    def test_classify_rate_limit_string(self):
        exc = Exception("429 Rate limit exceeded")
        err = self.classifier.classify(exc)
        assert isinstance(err, RateLimitError)
        assert err.retryable is True

    def test_classify_timeout_string(self):
        exc = Exception("Request timed out after 60s")
        err = self.classifier.classify(exc)
        assert isinstance(err, TimeoutError)

    def test_classify_unavailable_string(self):
        exc = Exception("Service unavailable: 503")
        err = self.classifier.classify(exc)
        assert isinstance(err, ProviderUnavailableError)

    def test_classify_connection_error_retryable(self):
        exc = ConnectionError("Connection refused")
        err = self.classifier.classify(exc)
        assert err.retryable is True

    def test_classify_generic_error_not_retryable(self):
        exc = Exception("Something weird happened")
        err = self.classifier.classify(exc)
        assert isinstance(err, ProviderError)
        assert err.retryable is False

    def test_is_retryable_true(self):
        err = RateLimitError()
        assert self.classifier.is_retryable(err) is True

    def test_is_retryable_false(self):
        err = AuthenticationError()
        assert self.classifier.is_retryable(err) is False

    def test_classify_with_openai_sdk_exception(self):
        try:
            import openai
            exc = openai.AuthenticationError(
                message="invalid api key",
                response=MagicMock(status_code=401, headers={}),
                body=None,
            )
            err = self.classifier.classify(exc, ProviderType.OPENAI)
            assert isinstance(err, AuthenticationError)
        except ImportError:
            pytest.skip("openai not installed")

    def test_classify_with_anthropic_sdk_exception(self):
        try:
            import anthropic
            exc = anthropic.AuthenticationError(
                message="invalid key",
                response=MagicMock(status_code=401, headers={}),
                body=None,
            )
            err = self.classifier.classify(exc, ProviderType.ANTHROPIC)
            assert isinstance(err, AuthenticationError)
        except (ImportError, TypeError):
            pytest.skip("anthropic not installed or incompatible")
