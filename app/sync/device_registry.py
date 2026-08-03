"""
Device Registry for Project Astra OS.
Tracks registered multi-device cluster nodes and device states.
"""

from typing import Dict, List, Optional, Any
import time
from app.models.device import DeviceNode, DeviceStatus


class DeviceRegistry:
    """
    Registry for cluster devices (Desktop, Laptop, Mobile).
    """

    def __init__(self, current_device_name: str = "Astra-Local-Node"):
        self._devices: Dict[str, DeviceNode] = {}
        self.local_device = self.register_device(current_device_name, platform="Windows")

    def register_device(self, name: str, platform: str = "Windows", ip_address: Optional[str] = "127.0.0.1") -> DeviceNode:
        """Registers a new device node."""
        node = DeviceNode(
            device_name=name,
            platform=platform,
            ip_address=ip_address,
            status=DeviceStatus.ONLINE
        )
        self._devices[node.device_id] = node
        return node

    def get_device(self, device_id: str) -> Optional[DeviceNode]:
        """Retrieves a device node."""
        return self._devices.get(device_id)

    def list_devices(self) -> List[Dict[str, Any]]:
        """Lists all registered devices."""
        return [d.to_dict() for d in self._devices.values()]

    def update_last_sync(self, device_id: str) -> bool:
        """Updates last_sync timestamp for a device."""
        device = self.get_device(device_id)
        if device:
            device.last_sync = time.time()
            device.status = DeviceStatus.ONLINE
            return True
        return False
