import logging
logger = logging.getLogger(__name__)

import anyio
import asyncio
import contextvars
import inspect
import threading

from anyio.from_thread import run as run_async_from_worker_thread
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, Union

# Used to represent the return type of the async function being decorated, 
# allowing syncable to be generic.
T = TypeVar("T")  

# Global thread portal for managing a persistent event loop
_global_event_loop = None
_global_event_loop_thread = None
_global_event_loop_lock = threading.Lock()


def get_global_event_loop():
    """
    Retrieve or create a global asyncio event loop running in a background thread.

    This function ensures that only one global event loop is created and shared across
    synchronous contexts that need to run asynchronous code. If the loop does not exist
    or is not running, it creates a new event loop and starts it in a dedicated daemon thread.

    Returns:
        asyncio.AbstractEventLoop: The global event loop instance.
    """
    global _global_event_loop, _global_event_loop_thread

    with _global_event_loop_lock:  # Ensure only one thread can create the loop at a time
        if _global_event_loop is None or not _global_event_loop.is_running():
            _global_event_loop = asyncio.new_event_loop()
            _global_event_loop_thread = threading.Thread(
                target=_run_event_loop, args=(_global_event_loop,), daemon=True
            )
            _global_event_loop_thread.start()

    return _global_event_loop


def _run_event_loop(loop):
    """
    Run the provided asyncio event loop in the current thread.

    This function is intended to be used as the target for a background thread.
    It sets the given event loop as the current thread's event loop and runs it forever.

    Args:
        loop (asyncio.AbstractEventLoop): The event loop to run.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()


def is_async_fn(func: Callable[..., Any]) -> bool:
    """
    Determine if a function is an async coroutine function.

    This function unwraps any decorators and checks if the underlying function
    is defined with `async def`.

    Args:
        func (Callable[..., Any]): The function to check.

    Returns:
        bool: True if the function is an async coroutine function, False otherwise.
    """
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return inspect.iscoroutinefunction(func)


def is_async_gen_fn(func: Callable[..., Any]) -> bool:
    """
    Determine if a function is an async generator function.

    This function unwraps any decorators and checks if the underlying function
    is defined as an async generator (`async def` with `yield`).

    Args:
        func (Callable[..., Any]): The function to check.

    Returns:
        bool: True if the function is an async generator function, False otherwise.
    """
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return inspect.isasyncgenfunction(func)


def in_async_main_thread() -> bool:
    """
    Check if the current context is running inside an asyncio event loop.

    Returns:
        bool: True if running inside an active asyncio event loop (i.e., in an async context),
              False otherwise.
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def in_async_worker_thread() -> bool:
    """
    Check if the current thread is an AnyIO async worker thread.

    This function inspects AnyIO's thread-local state to determine if the current
    thread is managed by AnyIO as an async worker. This relies on AnyIO internals
    and may break in future versions.

    Returns:
        bool: True if in an AnyIO async worker thread, False otherwise.
    """
    try:
        anyio.from_thread.threadlocals.current_async_backend
    except AttributeError:
        return False
    else:
        return True


def syncable(async_fn: Callable[..., Awaitable[T]]) -> Callable[..., Union[T, Awaitable[T]]]:
    """
    Decorator to make an async function callable from both sync and async contexts.

    When the returned function is called:
    - If in an async context, it returns the coroutine for the caller to await (type: Awaitable[T]).
    - If in a sync worker thread with access to an event loop, it submits the async
      function to the event loop and blocks until the result is available (type: T).
    - If in a sync context with no event loop, it creates a new event loop to run
      the async function and blocks until the result is available (type: T).

    Args:
        async_fn (Callable[..., Awaitable[T]]): The async function to decorate.

    Returns:
        Callable[..., Union[T, Awaitable[T]]]: A function that returns either the awaited result (T)
        or a coroutine (Awaitable[T]), depending on the calling context.

    Raises:
        TypeError: If the decorated function is not async.
        ValueError: If the decorated function is an async generator.
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
            ctx = contextvars.copy_context()
            coro = ctx.run(async_fn, *args, **kwargs)
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()

    # Attach the original async function for direct access if needed
    wrapper.aio = async_fn
    return wrapper