"""
Circuit Breaker Engine for Project Astra OS.
Implements CLOSED, OPEN, and HALF_OPEN state machine for external provider failover protection.
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
import time


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Tripped fail-fast state
    HALF_OPEN = "HALF_OPEN"  # Test recovery state


class CircuitBreaker:
    """
    Circuit Breaker state machine for API calls & external providers.
    """

    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 5.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Executes function wrapped with circuit breaker logic.
        """
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
            else:
                raise RuntimeError(f"CircuitBreaker '{self.name}' is OPEN. Request rejected to protect upstream service.")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = now
            return result
        except Exception as e:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = now
            raise e

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value if isinstance(self.state, CircuitState) else self.state,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold
        }
