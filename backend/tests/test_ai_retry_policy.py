"""Tests for RetryPolicy."""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from app.services.ai.error_classifier import (
    AuthenticationError,
    ProviderError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.services.ai.retry_policy import RetryPolicy


class TestRetryPolicy:
    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        policy = RetryPolicy(max_retries=3, base_delay=0.01)
        factory = AsyncMock(return_value="ok")
        result = await policy.execute(factory)
        assert result == "ok"
        assert factory.call_count == 1

    @pytest.mark.asyncio
    async def test_retryable_error_retries(self):
        policy = RetryPolicy(max_retries=2, base_delay=0.01, max_delay=0.1)
        factory = AsyncMock(side_effect=[ProviderUnavailableError("down"), "ok"])
        result = await policy.execute(factory)
        assert result == "ok"
        assert factory.call_count == 2

    @pytest.mark.asyncio
    async def test_non_retryable_error_raises_immediately(self):
        policy = RetryPolicy(max_retries=3, base_delay=0.01)
        factory = AsyncMock(side_effect=AuthenticationError("bad key"))
        with pytest.raises(AuthenticationError):
            await policy.execute(factory)
        assert factory.call_count == 1

    @pytest.mark.asyncio
    async def test_exhausted_retries_raises_last_error(self):
        policy = RetryPolicy(max_retries=2, base_delay=0.01, max_delay=0.1)
        factory = AsyncMock(side_effect=ProviderUnavailableError("down"))
        with pytest.raises(ProviderUnavailableError):
            await policy.execute(factory)
        assert factory.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_after_overrides_delay(self):
        policy = RetryPolicy(max_retries=1, base_delay=0.01, max_delay=0.1)
        error = RateLimitError("rate limited", retry_after=0.5)
        factory = AsyncMock(side_effect=[error, "ok"])

        with patch("app.services.ai.retry_policy.asyncio.sleep") as mock_sleep:
            result = await policy.execute(factory)
            assert result == "ok"
            assert mock_sleep.call_count == 1
            delay = mock_sleep.call_args[0][0]
            assert delay >= 0.5

    @pytest.mark.asyncio
    async def test_unknown_exception_classified_and_retried(self):
        policy = RetryPolicy(max_retries=1, base_delay=0.01, max_delay=0.1)
        factory = AsyncMock(side_effect=[ConnectionError("refused"), "ok"])
        result = await policy.execute(factory)
        assert result == "ok"
        assert factory.call_count == 2

    @pytest.mark.asyncio
    async def test_factory_called_multiple_times(self):
        call_count = 0

        async def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ProviderUnavailableError("fail")
            return "success"

        policy = RetryPolicy(max_retries=3, base_delay=0.01, max_delay=0.1)
        result = await policy.execute(flaky)
        assert result == "success"
        assert call_count == 3
