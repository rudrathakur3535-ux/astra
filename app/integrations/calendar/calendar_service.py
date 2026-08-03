"""
Google Calendar Service for Project Astra OS.
Reads upcoming events, creates meetings, and checks availability.
"""

from typing import List, Dict, Any, Optional
import time
from app.integrations.calendar.calendar_oauth import CalendarOAuthManager
from app.integrations.calendar.availability_engine import AvailabilityEngine
from app.models.calendar_context import CalendarEvent, ScheduleConflictReport


class CalendarService:
    """
    Calendar Service orchestrator.
    """

    def __init__(self, oauth_manager: Optional[CalendarOAuthManager] = None):
        self.oauth_manager = oauth_manager or CalendarOAuthManager()
        self.availability_engine = AvailabilityEngine()
        self._events: List[CalendarEvent] = [
            CalendarEvent(
                event_id="evt-001",
                summary="Architecture Sync Meeting",
                start_time=time.time() + 3600,
                end_time=time.time() + 7200,
                location="Google Meet",
                attendees=["team@astra.local"]
            )
        ]

    def get_upcoming_events(self) -> List[Dict[str, Any]]:
        """Returns upcoming calendar events."""
        return [e.to_dict() for e in self._events]

    def schedule_event(self, summary: str, start_time: float, duration_hours: float = 1.0) -> Dict[str, Any]:
        """
        Schedules a new meeting after verifying no conflicts exist.
        """
        end_time = start_time + (duration_hours * 3600.0)
        conflict_report = self.availability_engine.detect_conflicts(start_time, end_time, self._events)

        if conflict_report.has_conflict:
            return {
                "status": "conflict_detected",
                "message": f"Schedule conflict detected for '{summary}'.",
                "conflicting_events": [c.to_dict() for c in conflict_report.conflicting_events],
                "suggested_slots": conflict_report.suggested_slots
            }

        event = CalendarEvent(
            event_id=f"evt-{int(start_time)}",
            summary=summary,
            start_time=start_time,
            end_time=end_time
        )
        self._events.append(event)
        return {"status": "scheduled", "event": event.to_dict()}
