"""
Central Log Aggregator for Project Astra OS.
Aggregates, indexes, and queries structured application execution logs.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time
import uuid


@dataclass
class LogEntry:
    """Represents a structured log entry."""
    message: str
    level: str = "INFO"
    subsystem: str = "general"
    trace_id: Optional[str] = None
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp,
            "level": self.level.upper(),
            "subsystem": self.subsystem,
            "trace_id": self.trace_id,
            "message": self.message,
            "metadata": self.metadata
        }


class LogAggregator:
    """
    Central Log Aggregator for structured log storage, tailing, and filtering.
    """

    def __init__(self, max_entries: int = 5000):
        self._max_entries = max_entries
        self._logs: List[LogEntry] = []

    def log(
        self,
        message: str,
        level: str = "INFO",
        subsystem: str = "general",
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LogEntry:
        """
        Logs a structured message.
        """
        entry = LogEntry(
            message=message,
            level=level.upper(),
            subsystem=subsystem,
            trace_id=trace_id,
            metadata=metadata or {}
        )
        self._logs.append(entry)

        if len(self._logs) > self._max_entries:
            self._logs.pop(0)

        return entry

    def info(self, message: str, subsystem: str = "general", trace_id: Optional[str] = None, **kwargs) -> LogEntry:
        return self.log(message, level="INFO", subsystem=subsystem, trace_id=trace_id, metadata=kwargs)

    def warning(self, message: str, subsystem: str = "general", trace_id: Optional[str] = None, **kwargs) -> LogEntry:
        return self.log(message, level="WARNING", subsystem=subsystem, trace_id=trace_id, metadata=kwargs)

    def error(self, message: str, subsystem: str = "general", trace_id: Optional[str] = None, **kwargs) -> LogEntry:
        return self.log(message, level="ERROR", subsystem=subsystem, trace_id=trace_id, metadata=kwargs)

    def debug(self, message: str, subsystem: str = "general", trace_id: Optional[str] = None, **kwargs) -> LogEntry:
        return self.log(message, level="DEBUG", subsystem=subsystem, trace_id=trace_id, metadata=kwargs)

    def query(
        self,
        level: Optional[str] = None,
        subsystem: Optional[str] = None,
        trace_id: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Queries and filters logs.
        """
        results = self._logs

        if level:
            level_upper = level.upper()
            results = [l for l in results if l.level == level_upper]

        if subsystem:
            results = [l for l in results if l.subsystem.lower() == subsystem.lower()]

        if trace_id:
            results = [l for l in results if l.trace_id == trace_id]

        if search_query:
            query_lower = search_query.lower()
            results = [l for l in results if query_lower in l.message.lower()]

        # Return latest matching entries up to limit
        return [entry.to_dict() for entry in results[-limit:]]

    def tail(self, count: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent N log entries."""
        return [entry.to_dict() for entry in self._logs[-count:]]

    def get_error_count(self) -> int:
        """Returns total error logs recorded."""
        return sum(1 for entry in self._logs if entry.level in ("ERROR", "CRITICAL"))

    def clear(self) -> None:
        """Clears all stored logs."""
        self._logs.clear()
