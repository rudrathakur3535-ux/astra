"""
Device Registration Model for Project Astra OS.
Represents multi-device cluster profiles and node statuses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"


@dataclass
class DeviceNode:
    """
    Registered device node profile.
    """
    device_name: str
    platform: str = "Windows"
    device_id: str = field(default_factory=lambda: f"dev-{uuid.uuid4().hex[:8]}")
    ip_address: Optional[str] = "127.0.0.1"
    status: DeviceStatus = DeviceStatus.ONLINE
    last_sync: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "platform": self.platform,
            "ip_address": self.ip_address,
            "status": self.status.value if isinstance(self.status, DeviceStatus) else self.status,
            "last_sync": self.last_sync,
            "registered_at": self.registered_at,
            "metadata": self.metadata
        }
