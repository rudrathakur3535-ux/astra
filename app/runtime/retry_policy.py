"""
Retry Policy Module for Project Astra.
Provides configurable retry strategies (IMMEDIATE, FIXED_DELAY, EXPONENTIAL_BACKOFF).
"""

from enum import Enum
import time
import asyncio
from app.utils.logger import logger


class RetryStrategy(str, Enum):
    IMMEDIATE = "immediate"
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


class RetryPolicy:
    """
    Configurable retry policy manager for step execution failures.
    """

    def __init__(
        self,
        max_retries: int = 3,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay_sec: float = 1.0,
        max_delay_sec: float = 10.0
    ):
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay_sec = base_delay_sec
        self.max_delay_sec = max_delay_sec

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculates delay duration in seconds for a given attempt index (1-based).
        """
        if self.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.strategy == RetryStrategy.FIXED_DELAY:
            return self.base_delay_sec
        elif self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay_sec * (2 ** (attempt - 1))
            return min(delay, self.max_delay_sec)
        return 0.0

    async def wait_before_retry(self, attempt: int) -> None:
        """
        Asynchronously pauses execution before retrying.
        """
        delay = self.calculate_delay(attempt)
        if delay > 0:
            logger.info(f"[RetryPolicy] Waiting {delay:.2f}s before retry attempt {attempt}/{self.max_retries}...")
            await asyncio.sleep(delay)
