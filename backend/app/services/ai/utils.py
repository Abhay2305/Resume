"""Utility functions for the AI engine."""
import asyncio
import threading
from typing import Any, Coroutine


def run_async(coro: Coroutine) -> Any:
    """Run an async coroutine from synchronous code safely.

    Handles all contexts:
    - Plain synchronous thread (no event loop): creates a new loop
    - AnyIO worker thread (FastAPI background): spawns a new thread with its own loop
    - Already in an async context: uses loop.run_until_complete

    This is the ONLY correct way to call async code from sync wrappers.
    """

    def _run_in_new_thread(coro_obj):
        result = [None]
        exception = [None]

        def _target():
            try:
                result[0] = asyncio.run(coro_obj)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join()
        if exception[0] is not None:
            raise exception[0]
        return result[0]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        return _run_in_new_thread(coro)
    else:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("closed")
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            return _run_in_new_thread(coro)
        elif loop is not None:
            return loop.run_until_complete(coro)
        else:
            return asyncio.run(coro)
