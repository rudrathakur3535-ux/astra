"""
Crash Reporter for Project Astra OS.
Captures exception stack traces, logs crash events, and correlates Trace IDs.
"""

from typing import Dict, Any, Optional, List
import traceback
import time
import uuid
from app.observability.log_aggregator import LogAggregator


class CrashReporter:
    """
    Captures, logs, and aggregates application runtime crash exceptions.
    """

    def __init__(self, log_aggregator: Optional[LogAggregator] = None):
        self.log_aggregator = log_aggregator or LogAggregator()
        self._crashes: List[Dict[str, Any]] = []

    def record_crash(
        self,
        exception: Exception,
        subsystem: str = "runtime",
        trace_id: Optional[str] = None,
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Captures an exception stack trace and correlates it with a Trace ID.
        """
        formatted_tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
        stack_str = "".join(formatted_tb)

        crash_entry = {
            "crash_id": f"crash-{uuid.uuid4().hex[:8]}",
            "timestamp": time.time(),
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "subsystem": subsystem,
            "trace_id": trace_id,
            "stack_trace": stack_str,
            "metadata": context_metadata or {}
        }

        self._crashes.append(crash_entry)
        self.log_aggregator.error(
            message=f"CRASH RECORDED in {subsystem}: {type(exception).__name__}: {str(exception)}",
            subsystem=subsystem,
            trace_id=trace_id,
            crash_id=crash_entry["crash_id"]
        )

        return crash_entry

    def get_crashes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent crash reports."""
        return self._crashes[-limit:]

    def get_crash_count(self) -> int:
        """Returns total crash count."""
        return len(self._crashes)
