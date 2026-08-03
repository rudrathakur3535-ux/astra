"""
Health Status Model for Project Astra.
Represents real-time subsystem health states and latency reports.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class SubsystemHealth:
    """
    Subsystem health status report.
    """
    subsystem_name: str
    state: HealthState = HealthState.HEALTHY
    latency_ms: float = 0.0
    details: str = "Operating normally."
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem_name": self.subsystem_name,
            "state": self.state.value if isinstance(self.state, HealthState) else self.state,
            "latency_ms": round(self.latency_ms, 2),
            "details": self.details,
            "metadata": self.metadata,
            "last_check": self.last_check
        }
