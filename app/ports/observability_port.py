"""
Observability Port Interface for Project Astra (Hexagonal Architecture).
Enforces strict decoupling between core observability logic and storage/monitoring backends.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.metric import Metric
from app.models.trace import TraceSpan
from app.models.health_status import SubsystemHealth
from app.models.timeline_event import TimelineEvent


class ObservabilityPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Observability Adapters.
    """

    @abstractmethod
    def record_metric(self, metric: Metric) -> None:
        """Records a metric measurement."""
        pass

    @abstractmethod
    def record_span(self, span: TraceSpan) -> None:
        """Records a distributed tracing span."""
        pass

    @abstractmethod
    def get_trace_spans(self, trace_id: str) -> List[TraceSpan]:
        """Retrieves all spans associated with a trace ID."""
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, SubsystemHealth]:
        """Retrieves overall subsystem health status."""
        pass

    @abstractmethod
    def add_timeline_event(self, event: TimelineEvent) -> None:
        """Adds a timeline event."""
        pass
