"""
Calendar Availability & Conflict Engine for Project Astra OS.
Detects schedule conflicts and finds free meeting slots.
"""

from typing import List, Dict, Any, Optional
import time
from app.models.calendar_context import CalendarEvent, ScheduleConflictReport


class AvailabilityEngine:
    """
    Schedule conflict detector and free slot finder.
    """

    def detect_conflicts(self, new_start: float, new_end: float, existing_events: List[CalendarEvent]) -> ScheduleConflictReport:
        """
        Checks if a requested event conflicts with existing events.
        """
        conflicts = []
        for ev in existing_events:
            # Overlap condition: start < ev.end and end > ev.start
            if new_start < ev.end_time and new_end > ev.start_time:
                conflicts.append(ev)

        has_conflict = len(conflicts) > 0
        suggested = []
        if has_conflict:
            # Suggest next available slot 1 hour after latest conflict
            max_end = max(ev.end_time for ev in conflicts)
            suggested.append({
                "start_time": max_end + 1800.0,
                "end_time": max_end + 1800.0 + (new_end - new_start)
            })

        return ScheduleConflictReport(
            has_conflict=has_conflict,
            conflicting_events=conflicts,
            suggested_slots=suggested
        )
