"""
Calendar Service Module for Project Astra.
Manages schedule event creation, schedule retrieval, and overlapping event conflict detection.
"""

from typing import List, Optional, Dict, Any, Tuple
import time

from app.adapters.calendar_adapter import CalendarAdapter
from app.models.calendar_event import CalendarEvent
from app.utils.logger import logger


class CalendarService:
    """
    Calendar service managing schedule events and detecting time conflicts.
    """

    def __init__(self, adapter: Optional[CalendarAdapter] = None):
        self.adapter = adapter or CalendarAdapter()

    def get_schedule(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[CalendarEvent]:
        """Returns events for a given time window (defaults to today)."""
        now = start_time or time.time()
        window_end = end_time or (now + 86400)  # 24 hours
        return self.adapter.list_events(now, window_end)

    def detect_conflicts(self, proposed_event: CalendarEvent) -> List[CalendarEvent]:
        """
        Scans existing events and returns any overlapping calendar conflicts.
        """
        existing = self.adapter.list_events(proposed_event.start_time - 86400, proposed_event.end_time + 86400)
        conflicts = [e for e in existing if proposed_event.is_overlapping_with(e)]

        if conflicts:
            logger.warning(f"[CalendarService] Conflict detected! Proposed event '{proposed_event.title}' overlaps with {len(conflicts)} existing events.")
        return conflicts

    def schedule_event(self, event: CalendarEvent, allow_conflicts: bool = False) -> Tuple[bool, List[CalendarEvent]]:
        """
        Schedules a new event after checking for time conflicts.

        Returns:
            Tuple[bool, List[CalendarEvent]]: (success, conflicting_events)
        """
        conflicts = self.detect_conflicts(event)
        if conflicts and not allow_conflicts:
            return False, conflicts

        created = self.adapter.create_event(event)
        return created, conflicts
