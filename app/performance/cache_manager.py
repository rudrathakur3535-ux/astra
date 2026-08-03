"""
Multi-Tier LRU Cache Manager for Project Astra OS.
Provides prompt response cache, vector embedding cache, tool result cache, and session cache.
"""

from typing import Dict, Any, Optional
from collections import OrderedDict
import time


class LRUCache:
    """Bounded LRU Cache data structure."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            self.misses += 1
            return None
        self.hits += 1
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def size(self) -> int:
        return len(self._cache)


class CacheManager:
    """
    Master Multi-Level Caching Subsystem.
    """

    def __init__(self):
        self.prompt_cache = LRUCache(capacity=200)
        self.embedding_cache = LRUCache(capacity=500)
        self.tool_cache = LRUCache(capacity=100)
        self.session_cache = LRUCache(capacity=50)

    def get_prompt(self, prompt: str) -> Optional[str]:
        return self.prompt_cache.get(prompt)

    def set_prompt(self, prompt: str, response: str) -> None:
        self.prompt_cache.set(prompt, response)

    def get_embedding(self, text: str) -> Optional[Any]:
        return self.embedding_cache.get(text)

    def set_embedding(self, text: str, embedding: Any) -> None:
        self.embedding_cache.set(text, embedding)

    def clear_all(self) -> None:
        self.prompt_cache.clear()
        self.embedding_cache.clear()
        self.tool_cache.clear()
        self.session_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "prompt_cache_size": self.prompt_cache.size(),
            "prompt_cache_hits": self.prompt_cache.hits,
            "embedding_cache_size": self.embedding_cache.size(),
            "tool_cache_size": self.tool_cache.size(),
            "session_cache_size": self.session_cache.size()
        }
