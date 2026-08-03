"""
Delta Sync Service for Project Astra OS.
Executes delta push and pull synchronization operations.
"""

from typing import List, Dict, Any, Optional
import time
from app.models.sync_event import SyncEvent
from app.sync.offline_queue import OfflineQueue
from app.sync.conflict_resolver import ConflictResolver, ConflictStrategy


class SyncService:
    """
    Delta Sync Engine.
    """

    def __init__(self, device_id: str = "dev-local-001"):
        self.device_id = device_id
        self.offline_queue = OfflineQueue()
        self.conflict_resolver = ConflictResolver()
        self._synced_events: List[SyncEvent] = []

    def create_event(self, entity_type: str, entity_id: str, payload: Dict[str, Any], action: str = "upsert") -> SyncEvent:
        """Creates a local sync event."""
        return SyncEvent(
            device_id=self.device_id,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload,
            action=action,
            timestamp=time.time()
        )

    def process_outgoing_event(self, event: SyncEvent, is_online: bool = True) -> bool:
        """Processes an outgoing event. If offline, enqueues to OfflineQueue."""
        if not is_online:
            self.offline_queue.enqueue(event)
            return False

        self._synced_events.append(event)
        return True

    def process_incoming_event(self, remote_event: SyncEvent, local_event: Optional[SyncEvent] = None) -> SyncEvent:
        """Processes an incoming event from another device, resolving conflicts if present."""
        if local_event:
            resolved = self.conflict_resolver.resolve(local_event, remote_event, strategy=ConflictStrategy.LATEST_WINS)
            self._synced_events.append(resolved)
            return resolved

        self._synced_events.append(remote_event)
        return remote_event

    def flush_offline_queue(self) -> int:
        """Flushes offline queue and pushes events."""
        events = self.offline_queue.flush()
        for evt in events:
            self._synced_events.append(evt)
        return len(events)
