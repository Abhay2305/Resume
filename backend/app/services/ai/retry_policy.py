"""Retry policy with exponential backoff and jitter."""
import asyncio
import random
from typing import Awaitable, Callable, Optional, TypeVar

from app.services.ai.error_classifier import ErrorClassifier, ProviderError, RateLimitError

T = TypeVar("T")


class RetryPolicy:
    """Executes async operations with retry, exponential backoff, and jitter."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        classifier: Optional[ErrorClassifier] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.classifier = classifier or ErrorClassifier()

    async def execute(self, coro_factory: Callable[[], Awaitable[T]]) -> T:
        """Execute an async operation with retries.

        Args:
            coro_factory: A callable that returns a new coroutine each time.
                Must be a factory because coroutines can only be awaited once.

        Returns:
            The result of the operation.

        Raises:
            The last exception if all retries are exhausted.
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return await coro_factory()
            except ProviderError as e:
                last_error = e
                if not e.retryable or attempt >= self.max_retries:
                    raise
                delay = self._calculate_delay(e, attempt)
                await asyncio.sleep(delay)
            except Exception as e:
                classified = self.classifier.classify(e)
                last_error = classified
                if not classified.retryable or attempt >= self.max_retries:
                    raise classified
                delay = self._calculate_delay(classified, attempt)
                await asyncio.sleep(delay)

        if last_error:
            raise last_error
        raise ProviderError("Retry exhausted")

    def _calculate_delay(self, error: ProviderError, attempt: int) -> float:
        delay = min(
            self.base_delay * (2 ** attempt) + random.uniform(0, self.base_delay),
            self.max_delay,
        )
        if isinstance(error, RateLimitError) and error.retry_after:
            delay = max(delay, error.retry_after)
        return delay
