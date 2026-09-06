"""Tests for ResponseCache."""
import asyncio
import pytest
from app.services.ai.response_cache import CachedResponse, ResponseCache


def _make_response(content="test", model="gpt-4o", provider="openai"):
    return CachedResponse(
        content=content,
        model=model,
        provider=provider,
        usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        finish_reason="stop",
        latency_ms=100.0,
        request_id="req-1",
    )


class TestResponseCache:
    @pytest.mark.asyncio
    async def test_cache_hit(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=3600)
        key = "test-key"
        resp = _make_response()
        await cache.set(key, resp)
        result = await cache.get(key)
        assert result is not None
        assert result.content == "test"
        assert cache.hits == 1
        assert cache.misses == 0

    @pytest.mark.asyncio
    async def test_cache_miss(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=3600)
        result = await cache.get("nonexistent")
        assert result is None
        assert cache.misses == 1

    @pytest.mark.asyncio
    async def test_ttl_expiry(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=1)
        key = "test-key"
        await cache.set(key, _make_response())
        # Manually backdate the stored time
        response, _ = cache._cache[key]
        cache._cache[key] = (response, 0.0)  # epoch = long ago
        result = await cache.get(key)
        assert result is None
        assert cache.misses == 1

    @pytest.mark.asyncio
    async def test_ttl_zero_means_no_expiry(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=0)
        key = "test-key"
        await cache.set(key, _make_response())
        result = await cache.get(key)
        assert result is not None

    @pytest.mark.asyncio
    async def test_lru_eviction(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=2, ttl=3600)
        await cache.set("k1", _make_response(content="a"))
        await cache.set("k2", _make_response(content="b"))
        await cache.get("k1")  # access k1 to make it recently used
        await cache.set("k3", _make_response(content="c"))  # should evict k2
        assert await cache.get("k1") is not None
        assert await cache.get("k2") is None
        assert await cache.get("k3") is not None

    @pytest.mark.asyncio
    async def test_invalidate_by_model(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=3600)
        await cache.set("k1", _make_response(model="gpt-4o"))
        await cache.set("k2", _make_response(model="gemini-2.0-flash"))
        removed = await cache.invalidate(model="gpt-4o")
        assert removed == 1
        assert await cache.get("k1") is None
        assert await cache.get("k2") is not None

    @pytest.mark.asyncio
    async def test_clear(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=3600)
        await cache.set("k1", _make_response())
        await cache.set("k2", _make_response())
        count = await cache.clear()
        assert count == 2
        assert cache.size == 0

    @pytest.mark.asyncio
    async def test_hit_rate(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=10, ttl=3600)
        await cache.set("k1", _make_response())
        await cache.get("k1")
        await cache.get("k2")
        assert cache.hit_rate == 0.5

    @pytest.mark.asyncio
    async def test_disabled_cache(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "false")
        cache = ResponseCache(max_entries=10, ttl=3600)
        await cache.set("k1", _make_response())
        result = await cache.get("k1")
        assert result is None

    @pytest.mark.asyncio
    async def test_concurrent_access(self, monkeypatch):
        monkeypatch.setenv("AI_CACHE_ENABLED", "true")
        cache = ResponseCache(max_entries=100, ttl=3600)

        async def writer(n):
            await cache.set(f"k{n}", _make_response(content=str(n)))

        async def reader(n):
            return await cache.get(f"k{n}")

        await asyncio.gather(*[writer(i) for i in range(50)])
        results = await asyncio.gather(*[reader(i) for i in range(50)])
        assert all(r is not None for r in results)

    def test_make_key_deterministic(self):
        messages = [{"role": "user", "content": "hello"}]
        k1 = ResponseCache.make_key(messages, "gpt-4o", 0.7, 1024)
        k2 = ResponseCache.make_key(messages, "gpt-4o", 0.7, 1024)
        assert k1 == k2

    def test_make_key_varies_with_user_id(self):
        messages = [{"role": "user", "content": "hello"}]
        k1 = ResponseCache.make_key(messages, "gpt-4o", 0.7, 1024, user_id="u1")
        k2 = ResponseCache.make_key(messages, "gpt-4o", 0.7, 1024, user_id="u2")
        assert k1 != k2

    def test_make_key_varies_with_model(self):
        messages = [{"role": "user", "content": "hello"}]
        k1 = ResponseCache.make_key(messages, "gpt-4o", 0.7, 1024)
        k2 = ResponseCache.make_key(messages, "gemini-2.0-flash", 0.7, 1024)
        assert k1 != k2
