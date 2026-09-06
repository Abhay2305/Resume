"""Tests for run_async utility."""
import asyncio
import pytest
from app.services.ai.utils import run_async


class TestRunAsync:
    def test_sync_context(self):
        async def coro():
            return 42
        result = run_async(coro())
        assert result == 42

    def test_sync_context_with_exception(self):
        async def coro():
            raise ValueError("test error")
        with pytest.raises(ValueError, match="test error"):
            run_async(coro())

    def test_nested_async_context(self):
        async def inner():
            return "inner"

        async def outer():
            return run_async(inner())

        result = run_async(outer())
        assert result == "inner"

    def test_returnsvarious_types(self):
        async def coro_dict():
            return {"key": "value"}

        async def coro_list():
            return [1, 2, 3]

        async def coro_none():
            return None

        assert run_async(coro_dict()) == {"key": "value"}
        assert run_async(coro_list()) == [1, 2, 3]
        assert run_async(coro_none()) is None
