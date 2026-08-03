"""
Conflict Resolver for Project Astra OS.
Resolves data sync conflicts using LATEST_WINS, MERGE, or MANUAL strategies.
"""

from typing import Dict, Any, Optional
from enum import Enum
from app.models.sync_event import SyncEvent


class ConflictStrategy(str, Enum):
    LATEST_WINS = "latest_wins"
    MERGE = "merge"
    MANUAL = "manual"


class ConflictResolver:
    """
    Data conflict resolution engine.
    """

    def resolve(
        self,
        local_event: SyncEvent,
        remote_event: SyncEvent,
        strategy: ConflictStrategy = ConflictStrategy.LATEST_WINS
    ) -> SyncEvent:
        """
        Resolves a conflict between a local and remote sync event.
        """
        if strategy == ConflictStrategy.LATEST_WINS:
            if remote_event.timestamp >= local_event.timestamp:
                return remote_event
            return local_event

        elif strategy == ConflictStrategy.MERGE:
            merged_payload = dict(local_event.payload)
            merged_payload.update(remote_event.payload)

            return SyncEvent(
                device_id=local_event.device_id,
                entity_type=local_event.entity_type,
                entity_id=local_event.entity_id,
                payload=merged_payload,
                action="upsert",
                timestamp=max(local_event.timestamp, remote_event.timestamp)
            )

        # MANUAL -> default fallback to remote with flag
        merged = dict(remote_event.payload)
        merged["_conflict_flag"] = "manual_review_required"
        remote_event.payload = merged
        return remote_event
