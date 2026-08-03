"""
Rate Limiter for Project Astra OS.
Implements Token Bucket and Sliding Window rate limiting policies.
"""

from typing import Dict, Any
import time


class RateLimiter:
    """
    Token Bucket Rate Limiter.
    """

    def __init__(self, max_tokens: int = 10, refill_rate_per_sec: float = 2.0):
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(max_tokens)
        self.last_refill = time.time()

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(float(self.max_tokens), self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

    def acquire(self, tokens_needed: int = 1) -> bool:
        """Attempts to consume tokens. Returns True if allowed, False if rate limit exceeded."""
        self._refill()
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False
