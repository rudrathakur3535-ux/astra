"""
Calendar Adapter for Project Astra.
Manages schedule event creation, retrieval, and calendar querying.
"""

from typing import List, Optional
import time

from app.models.calendar_event import CalendarEvent
from app.utils.logger import logger


class CalendarAdapter:
    """
    Calendar provider adapter.
    """

    def __init__(self):
        self._events: List[CalendarEvent] = []
        self._populate_demo_events()

    def _populate_demo_events(self) -> None:
        now = time.time()
        # Demo event 1: 1 hour from now
        self._events.append(CalendarEvent(
            title="Astra Engineering Standup",
            start_time=now + 3600,
            end_time=now + 7200,
            location="Google Meet",
            description="Daily sync on Astra OS v0.2 milestone progress.",
            attendees=["rudra@astra.os", "alex@astra.os"]
        ))
        # Demo event 2: 4 hours from now
        self._events.append(CalendarEvent(
            title="Architecture Review",
            start_time=now + 14400,
            end_time=now + 18000,
            location="Room 402",
            description="Review Communication Platform ADR 007.",
            attendees=["rudra@astra.os"]
        ))

    def list_events(self, start_time: float, end_time: float) -> List[CalendarEvent]:
        matching = [
            e for e in self._events
            if e.end_time >= start_time and e.start_time <= end_time
        ]
        return matching

    def create_event(self, event: CalendarEvent) -> bool:
        self._events.append(event)
        logger.info(f"[CalendarAdapter] Created calendar event '{event.title}' at {time.ctime(event.start_time)}")
        return True
