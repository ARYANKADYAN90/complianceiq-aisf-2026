import asyncio
import time

class RateLimiter:
    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls_per_minute = max_calls_per_minute
        self.interval = 60.0 / max_calls_per_minute
        self.last_call_time = 0.0
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_call_time
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self.last_call_time = time.time()
