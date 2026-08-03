"""
Graceful Shutdown Handler for Project Astra OS.
Flushes buffers, completes database writes, and terminates worker threads safely.
"""

from typing import Dict, Any, List, Callable
import time


class GracefulShutdownManager:
    """
    Manages orderly shutdown hooks for Astra OS components.
    """

    def __init__(self):
        self._hooks: List[Callable[[], None]] = []
        self.is_shutting_down = False

    def register_shutdown_hook(self, hook_fn: Callable[[], None]) -> None:
        """Registers a cleanup hook to run on shutdown."""
        self._hooks.append(hook_fn)

    def trigger_graceful_shutdown(self) -> Dict[str, Any]:
        """Executes registered shutdown hooks safely."""
        self.is_shutting_down = True
        executed = 0
        failed = 0

        for hook in self._hooks:
            try:
                hook()
                executed += 1
            except Exception:
                failed += 1

        return {
            "status": "shutdown_complete",
            "hooks_executed": executed,
            "hooks_failed": failed,
            "timestamp": time.time()
        }
