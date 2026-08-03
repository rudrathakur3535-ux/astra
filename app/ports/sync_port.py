"""
Sync Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.sync_event import SyncEvent
from app.models.device import DeviceNode


class SyncPort(ABC):
    """
    Abstract Hexagonal Port interface for Sync Adapters.
    """

    @abstractmethod
    def push_events(self, device_id: str, events: List[SyncEvent]) -> bool:
        """Pushes delta sync events to remote cloud/cluster endpoint."""
        pass

    @abstractmethod
    def pull_events(self, device_id: str, since_timestamp: float) -> List[SyncEvent]:
        """Pulls delta sync events from remote endpoint."""
        pass

    @abstractmethod
    def register_device(self, device: DeviceNode) -> bool:
        """Registers a device node with sync cluster."""
        pass
