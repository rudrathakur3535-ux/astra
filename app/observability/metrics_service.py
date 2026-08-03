"""
Metrics Service for Project Astra OS.
Provides live metrics collection (counters, gauges, histograms),
high-latency alert callbacks, and metric aggregation.
"""

from typing import Dict, List, Any, Optional, Callable
import time
from collections import defaultdict
from app.models.metric import Metric, MetricType
from app.ports.observability_port import ObservabilityPort


class MetricsService:
    """
    Live Metrics Service for recording and retrieving operational metrics.
    """

    def __init__(self, port: Optional[ObservabilityPort] = None, high_latency_threshold_ms: float = 2000.0):
        self._port = port
        self._metrics: List[Metric] = []
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._high_latency_threshold_ms = high_latency_threshold_ms
        self._alert_callbacks: List[Callable[[str, float], None]] = []

    def register_alert_callback(self, callback: Callable[[str, float], None]) -> None:
        """Registers a callback for high latency alerts."""
        self._alert_callbacks.append(callback)

    def record_metric(self, metric: Metric) -> None:
        """
        Records an individual metric measurement.
        """
        self._metrics.append(metric)

        if metric.metric_type == MetricType.COUNTER:
            self._counters[metric.name] += metric.value
        elif metric.metric_type == MetricType.GAUGE:
            self._gauges[metric.name] = metric.value
        elif metric.metric_type == MetricType.HISTOGRAM:
            self._histograms[metric.name].append(metric.value)
            if metric.value > self._high_latency_threshold_ms:
                self._trigger_latency_alert(metric.name, metric.value)

        if self._port:
            self._port.record_metric(metric)

    def _trigger_latency_alert(self, metric_name: str, latency_ms: float) -> None:
        """Triggers alert callbacks when a metric exceeds the high-latency threshold."""
        for cb in self._alert_callbacks:
            try:
                cb(metric_name, latency_ms)
            except Exception:
                pass

    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Records a counter metric."""
        metric = Metric(name=name, value=value, metric_type=MetricType.COUNTER, tags=tags or {})
        self.record_metric(metric)

    def record_gauge(self, name: str, value: float, unit: str = "", tags: Optional[Dict[str, str]] = None) -> None:
        """Records a gauge metric."""
        metric = Metric(name=name, value=value, metric_type=MetricType.GAUGE, unit=unit, tags=tags or {})
        self.record_metric(metric)

    def record_latency(self, name: str, latency_ms: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Records a latency measurement in milliseconds (histogram)."""
        metric = Metric(name=name, value=latency_ms, metric_type=MetricType.HISTOGRAM, unit="ms", tags=tags or {})
        self.record_metric(metric)

    # Core Astra Helper Recorders
    def record_llm_latency(self, latency_ms: float, model: str = "default") -> None:
        self.record_latency("llm_latency_ms", latency_ms, tags={"model": model})

    def record_token_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.record_counter("llm_prompt_tokens", float(prompt_tokens))
        self.record_counter("llm_completion_tokens", float(completion_tokens))
        self.record_counter("llm_total_tokens", float(prompt_tokens + completion_tokens))

    def record_memory_retrieval(self, duration_ms: float, results_count: int) -> None:
        self.record_latency("memory_retrieval_ms", duration_ms)
        self.record_counter("memory_retrieval_count", 1.0)
        self.record_gauge("memory_results_returned", float(results_count))

    def record_knowledge_retrieval(self, duration_ms: float, hits: int) -> None:
        self.record_latency("knowledge_retrieval_ms", duration_ms)
        self.record_counter("knowledge_retrieval_count", 1.0)
        self.record_gauge("knowledge_hits", float(hits))

    def record_tool_latency(self, tool_name: str, latency_ms: float, success: bool = True) -> None:
        self.record_latency("tool_latency_ms", latency_ms, tags={"tool": tool_name})
        status = "success" if success else "failure"
        self.record_counter("tool_execution_total", 1.0, tags={"tool": tool_name, "status": status})

    def record_plugin_latency(self, plugin_name: str, latency_ms: float) -> None:
        self.record_latency("plugin_latency_ms", latency_ms, tags={"plugin": plugin_name})

    def record_workflow_duration(self, workflow_id: str, duration_ms: float, success: bool = True) -> None:
        self.record_latency("workflow_duration_ms", duration_ms, tags={"workflow_id": workflow_id})
        status = "success" if success else "failure"
        self.record_counter("workflow_executions_total", 1.0, tags={"status": status})

    def record_retry_count(self, operation: str, retries: int) -> None:
        self.record_counter("operation_retries_total", float(retries), tags={"operation": operation})

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns a summary dictionary of current metrics.
        """
        hist_stats = {}
        for name, values in self._histograms.items():
            if values:
                avg_val = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                hist_stats[name] = {
                    "count": len(values),
                    "avg": round(avg_val, 2),
                    "max": round(max_val, 2),
                    "min": round(min_val, 2)
                }

        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": hist_stats,
            "total_metrics_recorded": len(self._metrics)
        }

    def clear(self) -> None:
        """Clears all stored metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
