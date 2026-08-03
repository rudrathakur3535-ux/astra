"""
Timeout Manager Module for Project Astra.
Wraps async step tasks with configurable timeout limits to prevent hanging operations.
"""

import asyncio
from typing import Callable, Any, Coroutine, Optional
from app.utils.logger import logger


class TimeoutManager:
    """
    Manages timeout guardrails for async task execution.
    """

    def __init__(self, default_timeout_sec: float = 60.0):
        self.default_timeout_sec = default_timeout_sec

    async def execute_with_timeout(
        self,
        coro: Coroutine[Any, Any, Any],
        timeout_sec: Optional[float] = None
    ) -> Any:
        """
        Executes an async coroutine with a timeout.

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout duration.
        """
        limit = timeout_sec if timeout_sec is not None else self.default_timeout_sec
        try:
            return await asyncio.wait_for(coro, timeout=limit)
        except asyncio.TimeoutError:
            logger.error(f"[TimeoutManager] Task timed out after {limit}s limit.")
            raise
