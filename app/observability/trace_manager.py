"""
Distributed Trace Manager for Project Astra OS.
Tracks workflows and operations with unique Trace IDs and span hierarchies.
"""

from typing import Dict, List, Optional, Any
from contextlib import contextmanager, asynccontextmanager
import uuid
import time
from app.models.trace import TraceSpan, SpanStatus
from app.ports.observability_port import ObservabilityPort


class TraceManager:
    """
    Manages distributed tracing spans across multi-agent workflows.
    """

    def __init__(self, port: Optional[ObservabilityPort] = None):
        self._port = port
        self._spans_by_trace: Dict[str, List[TraceSpan]] = {}
        self._active_spans: Dict[str, TraceSpan] = {}

    def generate_trace_id(self) -> str:
        """Generates a unique Trace ID."""
        return f"trace-{uuid.uuid4().hex[:12]}"

    def start_trace(self, operation_name: str, tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """
        Starts a brand new root trace and returns the root span.
        """
        trace_id = self.generate_trace_id()
        return self.start_span(trace_id=trace_id, operation_name=operation_name, tags=tags)

    def start_span(
        self,
        trace_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TraceSpan:
        """
        Starts an execution span under a trace ID.
        """
        span = TraceSpan(
            trace_id=trace_id,
            operation_name=operation_name,
            parent_span_id=parent_span_id,
            tags=tags or {},
            metadata=metadata or {}
        )

        if trace_id not in self._spans_by_trace:
            self._spans_by_trace[trace_id] = []
        self._spans_by_trace[trace_id].append(span)
        self._active_spans[span.span_id] = span

        return span

    def finish_span(
        self,
        span: TraceSpan,
        status: SpanStatus = SpanStatus.OK,
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Finishes an active span.
        """
        if error:
            span.status = SpanStatus.ERROR
            span.metadata["error"] = str(error)
            span.metadata["error_type"] = type(error).__name__
        else:
            span.status = status

        if metadata:
            span.metadata.update(metadata)

        span.finish(span.status)
        self._active_spans.pop(span.span_id, None)

        if self._port:
            self._port.record_span(span)

    @contextmanager
    def span(
        self,
        trace_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Sync context manager for tracing a block of code.
        """
        span = self.start_span(trace_id, operation_name, parent_span_id, tags)
        try:
            yield span
            self.finish_span(span, status=SpanStatus.OK)
        except Exception as e:
            self.finish_span(span, status=SpanStatus.ERROR, error=e)
            raise

    @asynccontextmanager
    async def async_span(
        self,
        trace_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Async context manager for tracing an async block of code.
        """
        span = self.start_span(trace_id, operation_name, parent_span_id, tags)
        try:
            yield span
            self.finish_span(span, status=SpanStatus.OK)
        except Exception as e:
            self.finish_span(span, status=SpanStatus.ERROR, error=e)
            raise

    def get_trace_spans(self, trace_id: str) -> List[TraceSpan]:
        """Retrieves all spans for a specific trace ID."""
        if self._port:
            port_spans = self._port.get_trace_spans(trace_id)
            if port_spans:
                return port_spans
        return self._spans_by_trace.get(trace_id, [])

    def get_all_traces(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns all traces mapped to dicts."""
        result = {}
        for tid, spans in self._spans_by_trace.items():
            result[tid] = [s.to_dict() for s in spans]
        return result

    def get_active_trace_count(self) -> int:
        """Returns the count of active, unfinished spans."""
        return len(self._active_spans)
