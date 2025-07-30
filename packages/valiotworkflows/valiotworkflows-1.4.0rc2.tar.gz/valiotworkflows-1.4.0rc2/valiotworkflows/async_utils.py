"""
Utilities for the Asyncio Library and their utilities
to use it along with the Valiot Workflows
"""
# Create a ThreadPoolExecutor
import inspect
import asyncio
from typing import Callable, Awaitable, TypeVar, ParamSpec
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

executor = ThreadPoolExecutor()

P = ParamSpec('P')
R = TypeVar('R')


def to_async(
    func: Callable[P, R]
        | Callable[P, Awaitable[R]]
) -> Callable[P, Awaitable[R]]:
    '''
    Decorator to convert a blocking function to an async function

    :param func: The blocking function to convert
    :return: An async function

    example:
    ```@to_async
    def my_blocking_function():
        # This function is blocking and takes a long time to complete
        import time
        time.sleep(5)
        return "Blocking function completed"

    # Call the async function
    await my_blocking_function()
    ```
    '''
    if inspect.iscoroutinefunction(func) is True:
        return func  # type: ignore

    # For type checking, this is the best option to avoid thinking
    # that the function below is a Coroutine. The inspect doesn't provide
    # enough context to the type checker to tell it that the func should be here
    # a Callable and not a Coroutine
    no_async_func: Callable[P, R] = func  # type: ignore
    # If it is not asynchronous...

    @wraps(no_async_func)
    async def wrapper(*args, **kwargs) -> R:
        loop = asyncio.get_event_loop()
        # Run the blocking function in a ThreadPoolExecutor
        result = await loop.run_in_executor(executor, no_async_func, *args, **kwargs)
        return result
    return wrapper
