"""
Plugin Event Model for Project Astra.
Represents inter-plugin event payloads.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


@dataclass
class PluginEvent:
    """
    Event message sent or received by plugins.
    """
    event_type: str
    plugin_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "plugin_name": self.plugin_name,
            "data": self.data,
            "timestamp": self.timestamp
        }
