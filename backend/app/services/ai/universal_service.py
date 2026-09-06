"""UniversalAIService — the public orchestrator for AI operations.

Composes: TokenBudget → Cache → Registry → ProviderFactory → Retry → CostTracker
"""
import asyncio
import json
import logging
import re
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.services.ai.cost_tracker import CostTracker, estimate_cost
from app.services.ai.error_classifier import (
    AuthenticationError,
    ErrorClassifier,
    InvalidResponseError,
    ProviderError,
    ProviderUnavailableError,
    ResponseParsingError,
)
from app.services.ai.provider_factory import ProviderFactory
from app.services.ai.provider_registry import ProviderRegistry, _load_config
from app.services.ai.response_cache import CachedResponse, ResponseCache
from app.services.ai.retry_policy import RetryPolicy
from app.services.ai.token_budget import TokenBudget
from app.services.ai.types import ProviderConfig, ProviderMetrics, ProviderResponse, ProviderType

logger = logging.getLogger(__name__)


class UniversalAIService:
    """Public API for AI provider access. Orchestrates all sub-components."""

    def __init__(self, config: Optional[ProviderConfig] = None):
        self.config = config or _load_config()
        self._classifier = ErrorClassifier()
        self._retry = RetryPolicy(
            max_retries=self.config.max_retries,
            base_delay=self.config.retry_base_delay,
            max_delay=self.config.retry_max_delay,
            classifier=self._classifier,
        )
        self._cost_tracker = CostTracker()
        self._token_budget = TokenBudget()
        self._cache = ResponseCache()
        self._registry = ProviderRegistry()
        self._registry.register(self.config.provider_type, self.config)
        self._fallback_chain: List[ProviderConfig] = self._registry.get_fallback_chain()

    @property
    def provider_type(self) -> ProviderType:
        return self.config.provider_type

    @property
    def provider_name(self) -> str:
        return self.config.provider_type.value

    @property
    def model(self) -> str:
        return self.config.model or "unknown"

    @property
    def cache(self) -> ResponseCache:
        return self._cache

    @property
    def cost_tracker(self) -> CostTracker:
        return self._cost_tracker

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """Generate a response. Orchestrates: Budget → Cache → Fallback Chain → Retry → Cost."""
        request_id = kwargs.get("request_id", str(uuid.uuid4()))
        effective_temp = temperature if temperature is not None else self.config.temperature
        effective_max = max_tokens if max_tokens is not None else self.config.max_tokens

        # 1. Token Budget Check
        text_content = " ".join(m.get("content", "") for m in messages)
        self._token_budget.check_input(text_content)
        if user_id:
            estimated_tokens = self._token_budget.estimate_tokens(text_content)
            self._token_budget.check_user_daily(user_id, estimated_tokens)
            self._token_budget.check_user_monthly(user_id, estimated_tokens)

        # 2. Cache Lookup
        cache_key = ResponseCache.make_key(messages, self.model, effective_temp, effective_max, user_id)
        try:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.info(
                    "Cache hit: request_id=%s provider=%s model=%s",
                    cached.request_id, cached.provider, cached.model,
                )
                return ProviderResponse(
                    content=cached.content,
                    model=cached.model,
                    provider=ProviderType(cached.provider),
                    usage=cached.usage,
                    finish_reason=cached.finish_reason,
                    latency_ms=cached.latency_ms,
                    request_id=cached.request_id,
                )
        except Exception as e:
            logger.warning("Cache lookup failed (degrading to miss): %s", e)

        logger.info(
            "Cache miss: request_id=%s model=%s",
            request_id, self.model,
        )

        # 3. Fallback Chain Execution
        chain = self._fallback_chain
        if not chain:
            chain = [self.config]
        start_time = time.time()
        provider_errors: List[str] = []

        for provider_config in chain:
            provider = ProviderFactory.create(provider_config)
            provider_label = provider_config.provider_type.value

            async def _call_provider(p=provider, pc=provider_config):
                return await p.generate(
                    messages, pc.model, effective_temp, effective_max, **kwargs
                )

            try:
                response = await self._retry.execute(_call_provider)

                latency_ms = (time.time() - start_time) * 1000

                # Record fallback metrics if we fell back
                if provider_config.provider_type != self.config.provider_type:
                    self._cost_tracker.record_fallback(
                        from_provider=self.config.provider_type.value,
                        to_provider=provider_label,
                        succeeded=True,
                    )
                    logger.info(
                        "Fallback succeeded: %s → %s",
                        self.config.provider_type.value, provider_label,
                    )

                # 4. Record Metrics
                estimated = estimate_cost(provider_config.model, response.prompt_tokens, response.completion_tokens)
                metrics = ProviderMetrics(
                    request_id=request_id,
                    provider=provider_label,
                    model=provider_config.model,
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    total_tokens=response.total_tokens,
                    estimated_cost=estimated,
                    latency_ms=latency_ms,
                    success=True,
                )
                self._cost_tracker.record(metrics)

                # 5. Record token usage for user budgets
                if user_id:
                    self._token_budget.record_usage(user_id, response.total_tokens)

                # 6. Cache the response
                try:
                    cached_resp = CachedResponse(
                        content=response.content,
                        model=response.model,
                        provider=response.provider.value,
                        usage=response.usage,
                        finish_reason=response.finish_reason,
                        latency_ms=response.latency_ms,
                        request_id=response.request_id,
                    )
                    await self._cache.set(cache_key, cached_resp)
                except Exception as e:
                    logger.warning("Cache store failed: %s", e)

                logger.info(
                    "Request completed: request_id=%s provider=%s model=%s "
                    "prompt_tokens=%d completion_tokens=%d total_tokens=%d "
                    "cost=%.6f latency_ms=%.1f",
                    request_id, provider_label, provider_config.model,
                    response.prompt_tokens, response.completion_tokens,
                    response.total_tokens, estimated, latency_ms,
                )
                return response

            except ProviderError as e:
                provider_errors.append(f"{provider_label}: {e.message}")
                logger.warning(
                    "Provider %s failed (retryable=%s): %s",
                    provider_label, e.retryable, e.message,
                )

                # Record failed attempt metrics
                latency_ms = (time.time() - start_time) * 1000
                metrics = ProviderMetrics(
                    request_id=request_id,
                    provider=provider_label,
                    model=provider_config.model,
                    latency_ms=latency_ms,
                    success=False,
                    error_code=e.error_code,
                    error_message=str(e),
                )
                self._cost_tracker.record(metrics)

                # Record fallback metric
                if len(chain) > 1:
                    next_index = chain.index(provider_config) + 1
                    if next_index < len(chain):
                        next_provider = chain[next_index].provider_type.value
                    else:
                        next_provider = "none"
                    self._cost_tracker.record_fallback(
                        from_provider=provider_label,
                        to_provider=next_provider,
                        succeeded=False,
                    )

                continue

        # 4. All providers exhausted
        total_latency = (time.time() - start_time) * 1000
        error_chain = "; ".join(provider_errors)
        raise ProviderUnavailableError(
            f"All providers exhausted. Chain: [{error_chain}]",
            provider=self.config.provider_type,
        )

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream tokens. Budget check → fallback chain → delegate to provider."""
        request_id = kwargs.get("request_id", str(uuid.uuid4()))
        effective_temp = temperature if temperature is not None else self.config.temperature
        effective_max = max_tokens if max_tokens is not None else self.config.max_tokens

        logger.info(
            "Stream started: request_id=%s model=%s user_id=%s",
            request_id, self.model, user_id or "none",
        )

        text_content = " ".join(m.get("content", "") for m in messages)
        self._token_budget.check_input(text_content)
        if user_id:
            estimated_tokens = self._token_budget.estimate_tokens(text_content)
            self._token_budget.check_user_daily(user_id, estimated_tokens)
            self._token_budget.check_user_monthly(user_id, estimated_tokens)

        chain = self._fallback_chain
        if not chain:
            chain = [self.config]

        last_error: Optional[ProviderError] = None
        for provider_config in chain:
            provider = ProviderFactory.create(provider_config)
            provider_label = provider_config.provider_type.value
            start_time = time.time()
            try:
                stream = provider.generate_stream(
                    messages, provider_config.model, effective_temp, effective_max, **kwargs
                )
                aiter = stream.__aiter__()
                stream_error: Optional[ProviderError] = None
                while True:
                    try:
                        token = await aiter.__anext__()
                    except StopAsyncIteration:
                        break
                    except ProviderError as e:
                        stream_error = e
                        break
                    yield token
                if stream_error:
                    raise stream_error

                latency_ms = (time.time() - start_time) * 1000

                if provider_config.provider_type != self.config.provider_type:
                    self._cost_tracker.record_fallback(
                        from_provider=self.config.provider_type.value,
                        to_provider=provider_label,
                        succeeded=True,
                    )
                    logger.info(
                        "Stream fallback succeeded: %s → %s",
                        self.config.provider_type.value, provider_label,
                    )

                metrics = ProviderMetrics(
                    request_id=request_id,
                    provider=provider_label,
                    model=provider_config.model,
                    latency_ms=latency_ms,
                    success=True,
                )
                self._cost_tracker.record(metrics)

                logger.info(
                    "Stream completed: request_id=%s provider=%s model=%s latency_ms=%.1f",
                    request_id, provider_label, provider_config.model, latency_ms,
                )
                return
            except ProviderError as e:
                last_error = e
                logger.warning(
                    "Stream provider %s failed: %s",
                    provider_label, e.message,
                )

                latency_ms = (time.time() - start_time) * 1000
                metrics = ProviderMetrics(
                    request_id=request_id,
                    provider=provider_label,
                    model=provider_config.model,
                    latency_ms=latency_ms,
                    success=False,
                    error_code=e.error_code,
                    error_message=str(e),
                )
                self._cost_tracker.record(metrics)

                if len(chain) > 1:
                    next_index = chain.index(provider_config) + 1
                    if next_index < len(chain):
                        next_provider = chain[next_index].provider_type.value
                    else:
                        next_provider = "none"
                    self._cost_tracker.record_fallback(
                        from_provider=provider_label,
                        to_provider=next_provider,
                        succeeded=False,
                    )

                continue

        raise ProviderUnavailableError(
            "All providers failed for streaming",
            provider=self.config.provider_type,
        )

    async def health_check(self) -> bool:
        """Check if the configured provider is available."""
        try:
            provider = ProviderFactory.create(self.config)
            return await provider.health_check(self.config.api_key or "", self.model)
        except Exception as e:
            logger.debug("Health check failed: %s", e)
            return False

    def get_metrics_history(self) -> List[ProviderMetrics]:
        return self._cost_tracker.history()

    def get_metrics_summary(self) -> Dict[str, Any]:
        if not self._cost_tracker.history():
            return {"total_requests": 0, "provider": self.provider_name}

        s = self._cost_tracker.summary()
        budget = self._token_budget.get_budget_status()
        cache = self._cache
        return {
            "total_requests": s.total_requests,
            "successful": s.successful,
            "failed": s.failed,
            "success_rate": s.success_rate,
            "total_tokens": s.total_tokens,
            "total_cost_usd": s.total_cost_usd,
            "average_latency_ms": s.average_latency_ms,
            "provider": self.provider_name,
            "model": self.model,
            "budget": budget,
            "cache_hits": cache.hits,
            "cache_misses": cache.misses,
            "cache_hit_rate": cache.hit_rate,
        }

    def get_budget_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        return self._token_budget.get_budget_status(user_id)

    def get_budget_usage(self, user_id: Optional[str] = None) -> Dict[str, int]:
        return self._token_budget.get_budget_usage(user_id)

    def parse_json_response(self, content: str) -> Any:
        """Parse JSON from AI response, handling markdown wrapping."""
        if not content or not content.strip():
            raise ResponseParsingError("Empty content", provider=self.provider_type)

        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    continue

        raise ResponseParsingError(f"Failed to parse JSON: {cleaned[:200]}...", provider=self.provider_type)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_service_instance: Optional[UniversalAIService] = None


def get_ai_service() -> UniversalAIService:
    global _service_instance
    if _service_instance is None:
        _service_instance = UniversalAIService()
    return _service_instance


def reset_ai_service() -> None:
    global _service_instance
    _service_instance = None
