"""
Event Timeline Recorder for Project Astra OS.
Tracks sequential execution events and formats chronological timelines.
"""

from typing import List, Dict, Any, Optional
import time
from app.models.timeline_event import TimelineEvent
from app.ports.observability_port import ObservabilityPort


class EventTimeline:
    """
    Chronological Event Timeline for tracking and visualizing multi-step agent workflows.
    """

    def __init__(self, port: Optional[ObservabilityPort] = None):
        self._port = port
        self._events: List[TimelineEvent] = []

    def record_event(
        self,
        trace_id: str,
        category: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TimelineEvent:
        """
        Records a single timeline event.
        """
        event = TimelineEvent(
            trace_id=trace_id,
            category=category,
            message=message,
            metadata=metadata or {}
        )
        self._events.append(event)

        if self._port:
            self._port.add_timeline_event(event)

        return event

    def get_timeline_for_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Returns all timeline events for a trace ID sorted chronologically.
        """
        trace_events = [e for e in self._events if e.trace_id == trace_id]
        sorted_events = sorted(trace_events, key=lambda x: x.timestamp)
        return [e.to_dict() for e in sorted_events]

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns the N most recent timeline events sorted chronologically.
        """
        sorted_events = sorted(self._events, key=lambda x: x.timestamp)
        return [e.to_dict() for e in sorted_events[-limit:]]

    def clear(self) -> None:
        """Clears all recorded timeline events."""
        self._events.clear()
