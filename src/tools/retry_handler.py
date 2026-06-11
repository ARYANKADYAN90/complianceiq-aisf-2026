import asyncio
import random
import httpx
from typing import Callable, Any


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (httpx.TimeoutException, httpx.ConnectError),
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        raise e

                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    await asyncio.sleep(delay)
                except Exception as e:
                    raise e

        return wrapper

    return decorator
