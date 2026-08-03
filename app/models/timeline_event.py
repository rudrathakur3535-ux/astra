"""
Timeline Event Model for Project Astra.
Represents sequential execution timeline entries.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


@dataclass
class TimelineEvent:
    """
    Chronological event entry for workflow visualization.
    """
    trace_id: str
    category: str
    message: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "category": self.category,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
