import time
import hashlib
from collections import OrderedDict
from typing import Any


class CacheManager:
    def __init__(self, ttl: int = 300, max_entries: int = 100):
        self.ttl = ttl
        self.max_entries = max_entries
        self.cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def _generate_key(self, query_text: str, profile_hash: str = "") -> str:
        data = f"{query_text}:{profile_hash}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def get(self, query_text: str, profile_hash: str = "") -> Any:
        key = self._generate_key(query_text, profile_hash)
        if key in self.cache:
            timestamp, value = self.cache[key]
            if time.time() - timestamp <= self.ttl:
                self.cache.move_to_end(key)
                return value
            else:
                del self.cache[key]
        return None

    def set(self, query_text: str, value: Any, profile_hash: str = "") -> None:
        key = self._generate_key(query_text, profile_hash)
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (time.time(), value)
        if len(self.cache) > self.max_entries:
            self.cache.popitem(last=False)
