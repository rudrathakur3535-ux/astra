"""
Calendar Event Model for Project Astra.
Represents schedule entries, meeting invites, and calendar appointments.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import uuid


@dataclass
class CalendarEvent:
    """
    Represents a calendar event entry.
    """
    title: str
    start_time: float
    end_time: float
    location: str = ""
    description: str = ""
    attendees: List[str] = field(default_factory=list)
    is_all_day: bool = False
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def is_overlapping_with(self, other: "CalendarEvent") -> bool:
        """Checks if two calendar events overlap in time."""
        return max(self.start_time, other.start_time) < min(self.end_time, other.end_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "description": self.description,
            "attendees": self.attendees,
            "is_all_day": self.is_all_day,
            "created_at": self.created_at
        }
