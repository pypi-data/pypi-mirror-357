import logging
logger = logging.getLogger(__name__)

import anyio
import asyncio
import inspect
import threading

from anyio.from_thread import run as run_async_from_worker_thread
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, Union

T = TypeVar("T")
P = TypeVar("P")

# Global thread portal for managing a persistent event loop
_global_event_loop = None
_global_event_loop_thread = None


def get_global_event_loop():
    """
    Returns a global event loop for synchronous contexts. If no loop exists, it creates one.
    """
    global _global_event_loop, _global_event_loop_thread

    if _global_event_loop is None or not _global_event_loop.is_running():
        _global_event_loop = asyncio.new_event_loop()
        _global_event_loop_thread = threading.Thread(
            target=_run_event_loop, args=(_global_event_loop,), daemon=True
        )
        _global_event_loop_thread.start()

    return _global_event_loop


def _run_event_loop(loop):
    """
    Runs the event loop in a separate thread.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()


def is_async_fn(func: Callable[..., Any]) -> bool:
    """
    Returns `True` if a function is an async function.
    """
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return inspect.iscoroutinefunction(func)


def is_async_gen_fn(func: Callable[..., Any]) -> bool:
    """
    Returns `True` if a function is an async generator.
    """
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return inspect.isasyncgenfunction(func)


def in_async_main_thread() -> bool:
    """
    Returns `True` if the current thread is the main async thread.
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def in_async_worker_thread() -> bool:
    """
    Returns `True` if the current thread is an async worker thread.
    """
    try:
        anyio.from_thread.threadlocals.current_async_backend
    except AttributeError:
        return False
    else:
        return True


def syncable(async_fn: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """
    Converts an async function into a dual async and sync function.

    When the returned function is called:
    - If in an async context, it returns the coroutine for the caller to await.
    - If in a sync worker thread with access to an event loop, it submits the async
      function to the event loop.
    - If in a sync context with no event loop, it creates a new event loop to run
      the async function.
    """

    if not is_async_fn(async_fn):
        raise TypeError("The decorated function must be an async function.")
    if is_async_gen_fn(async_fn):
        raise ValueError("Async generators cannot be marked as `sync_compatible`.")

    @wraps(async_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Union[T, Awaitable[T]]:
        if in_async_main_thread():
            # In an async context, return the coroutine for the caller to await
            logger.debug(f"'{async_fn.__name__}' running in async context, returning coroutine.")
            return async_fn(*args, **kwargs)
        elif in_async_worker_thread():
            # In a sync worker thread, run the async function in the main thread's loop
            logger.debug(f"'{async_fn.__name__}' running in sync worker thread, execute the async function in the main thread's loop")
            return run_async_from_worker_thread(async_fn, *args, **kwargs)
        else:
            # In a sync context with no event loop, use the global event loop
            logger.debug(f"'{async_fn.__name__}' running in sync context with no event loop, using asyncio.run")
            loop = get_global_event_loop()
            future = asyncio.run_coroutine_threadsafe(async_fn(*args, **kwargs), loop)
            return future.result()

    # Attach the original async function for direct access if needed
    wrapper.aio = async_fn
    return wrapper