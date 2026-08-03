"""
Resource Snapshot Model for Project Astra OS.
Captures real-time CPU, RAM, Disk, active thread count, and queue length.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class ResourceSnapshot:
    cpu_percent: float
    ram_used_mb: float
    ram_percent: float
    disk_percent: float
    active_threads: int
    queue_size: int
    gpu_percent: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_percent": round(self.cpu_percent, 1),
            "ram_used_mb": round(self.ram_used_mb, 1),
            "ram_percent": round(self.ram_percent, 1),
            "disk_percent": round(self.disk_percent, 1),
            "active_threads": self.active_threads,
            "queue_size": self.queue_size,
            "gpu_percent": round(self.gpu_percent, 1) if self.gpu_percent is not None else None,
            "timestamp": self.timestamp
        }
