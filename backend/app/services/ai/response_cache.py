"""Async-safe exact-match response cache with TTL and LRU eviction."""
import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    finish_reason: str
    latency_ms: float
    request_id: str


class ResponseCache:
    """Async-safe in-memory cache for AI responses with TTL and LRU eviction."""

    def __init__(
        self,
        max_entries: Optional[int] = None,
        ttl: Optional[int] = None,
    ):
        enabled_str = os.getenv("AI_CACHE_ENABLED", "true").strip().lower()
        self._enabled = enabled_str not in ("false", "0", "no")

        self._max_entries = max_entries or int(os.getenv("AI_CACHE_MAX_ENTRIES", "1000"))
        self._ttl = ttl or int(os.getenv("AI_CACHE_TTL", "3600"))

        self._cache: Dict[str, Tuple[CachedResponse, float]] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._cache)

    @staticmethod
    def make_key(
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        user_id: Optional[str] = None,
    ) -> str:
        raw = json.dumps(messages, sort_keys=True) + model + str(temperature) + str(max_tokens) + (user_id or "")
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, key: str) -> Optional[CachedResponse]:
        if not self._enabled:
            return None
        try:
            async with self._lock:
                entry = self._cache.get(key)
                if entry is None:
                    self._misses += 1
                    return None
                response, stored_at = entry
                if self._ttl > 0 and (time.time() - stored_at) > self._ttl:
                    del self._cache[key]
                    if key in self._access_order:
                        self._access_order.remove(key)
                    self._misses += 1
                    return None
                self._hits += 1
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return response
        except Exception as e:
            logger.warning("Cache get failed (degrading to miss): %s", e)
            self._misses += 1
            return None

    async def set(self, key: str, response: CachedResponse) -> None:
        if not self._enabled:
            return
        try:
            async with self._lock:
                if key in self._cache:
                    if key in self._access_order:
                        self._access_order.remove(key)
                elif len(self._cache) >= self._max_entries:
                    self._evict_lru()
                self._cache[key] = (response, time.time())
                self._access_order.append(key)
        except Exception as e:
            logger.warning("Cache set failed: %s", e)

    async def invalidate(self, model: Optional[str] = None) -> int:
        removed = 0
        async with self._lock:
            keys_to_remove = []
            for key, (response, _) in self._cache.items():
                if model is None or response.model == model:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                removed += 1
        return removed

    async def clear(self) -> int:
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._access_order.clear()
            return count

    def _evict_lru(self) -> None:
        if self._access_order:
            oldest = self._access_order.pop(0)
            self._cache.pop(oldest, None)
