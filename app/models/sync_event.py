"""
Sync Event Model for Project Astra OS.
Represents delta synchronization events and entity payload updates across devices.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid
import hashlib
import json


@dataclass
class SyncEvent:
    """
    Delta Sync Event Payload.
    """
    device_id: str
    entity_type: str  # chat, memory, knowledge, settings, plugin, workflow
    entity_id: str
    payload: Dict[str, Any]
    action: str = "upsert"  # upsert, delete
    event_id: str = field(default_factory=lambda: f"syncevt-{uuid.uuid4().hex[:10]}")
    timestamp: float = field(default_factory=time.time)
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._generate_checksum()

    def _generate_checksum(self) -> str:
        data_str = f"{self.entity_type}:{self.entity_id}:{json.dumps(self.payload, sort_keys=True)}:{self.timestamp}"
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "device_id": self.device_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "action": self.action,
            "payload": self.payload,
            "checksum": self.checksum,
            "timestamp": self.timestamp
        }
