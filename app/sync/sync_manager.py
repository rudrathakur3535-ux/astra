"""
Master Sync Manager for Project Astra OS.
Orchestrates multi-device synchronization across chats, memory, knowledge, settings, plugins, and workflows.
"""

from typing import Dict, List, Any, Optional
from app.sync.device_registry import DeviceRegistry
from app.sync.sync_service import SyncService


class SyncManager:
    """
    Master Multi-Device Synchronization Orchestrator.
    """

    def __init__(self, device_name: str = "Astra-Master-Node"):
        self.registry = DeviceRegistry(current_device_name=device_name)
        self.service = SyncService(device_id=self.registry.local_device.device_id)

    def sync_entity(self, entity_type: str, entity_id: str, payload: Dict[str, Any], is_online: bool = True) -> Dict[str, Any]:
        """
        Synchronizes an entity update (chats, memory, knowledge, settings, plugins, workflows).
        """
        event = self.service.create_event(entity_type, entity_id, payload)
        success = self.service.process_outgoing_event(event, is_online=is_online)

        return {
            "status": "synced" if success else "queued_offline",
            "event_id": event.event_id,
            "checksum": event.checksum,
            "queued": not success
        }

    def sync_on_reconnect(self) -> Dict[str, Any]:
        """
        Triggers auto-sync of queued events when network reconnects.
        """
        flushed_count = self.service.flush_offline_queue()
        return {
            "status": "reconnected_and_synced",
            "flushed_events": flushed_count
        }

    def get_sync_summary(self) -> Dict[str, Any]:
        """Returns cluster device registry and sync status."""
        return {
            "local_device": self.registry.local_device.to_dict(),
            "devices": self.registry.list_devices(),
            "offline_queue_size": self.service.offline_queue.size(),
            "total_synced_events": len(self.service._synced_events)
        }
