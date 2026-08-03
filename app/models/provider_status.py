"""
Provider Status Model for Project Astra OS.
Represents AI LLM Provider health reports, latencies, and local/cloud flags.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time


class ProviderState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass
class ProviderStatus:
    """
    AI LLM Provider health report.
    """
    provider_name: str
    state: ProviderState = ProviderState.HEALTHY
    latency_ms: float = 0.0
    is_local: bool = False
    privacy_rating: str = "standard"  # local_private, encrypted_cloud, standard
    last_check: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "state": self.state.value if isinstance(self.state, ProviderState) else self.state,
            "latency_ms": round(self.latency_ms, 2),
            "is_local": self.is_local,
            "privacy_rating": self.privacy_rating,
            "last_check": self.last_check,
            "metadata": self.metadata
        }
