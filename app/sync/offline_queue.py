"""
Offline Queue Engine for Project Astra OS.
Buffers sync events offline and automatically flushes them upon network reconnection.
"""

from typing import List, Dict, Any, Optional
from app.models.sync_event import SyncEvent


class OfflineQueue:
    """
    Resilient offline sync event queue.
    """

    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self._queue: List[SyncEvent] = []

    def enqueue(self, event: SyncEvent) -> bool:
        """Enqueues a sync event while offline."""
        if len(self._queue) >= self.max_queue_size:
            self._queue.pop(0)
        self._queue.append(event)
        return True

    def get_queued_events(self) -> List[SyncEvent]:
        """Returns buffered queued events."""
        return list(self._queue)

    def flush(self) -> List[SyncEvent]:
        """Flushes and returns all queued events for synchronization."""
        events = list(self._queue)
        self._queue.clear()
        return events

    def size(self) -> int:
        """Returns current queue size."""
        return len(self._queue)
