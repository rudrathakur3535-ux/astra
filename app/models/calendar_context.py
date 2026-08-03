"""
Calendar Context Model for Project Astra OS.
Represents Google Calendar events, schedule slots, and conflict reports.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class CalendarEvent:
    event_id: str
    summary: str
    start_time: float
    end_time: float
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "summary": self.summary,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "attendees": self.attendees,
            "duration_mins": round((self.end_time - self.start_time) / 60.0, 1)
        }


@dataclass
class ScheduleConflictReport:
    has_conflict: bool
    conflicting_events: List[CalendarEvent] = field(default_factory=list)
    suggested_slots: List[Dict[str, float]] = field(default_factory=list)
