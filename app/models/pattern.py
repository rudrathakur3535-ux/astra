"""
User Pattern Model for Project Astra OS.
Represents mined interaction patterns and time-window frequencies.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class Pattern:
    pattern_id: str
    event_type: str
    occurrences: int
    time_window: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "event_type": self.event_type,
            "occurrences": self.occurrences,
            "time_window": self.time_window,
            "metadata": self.metadata,
            "detected_at": self.detected_at
        }
