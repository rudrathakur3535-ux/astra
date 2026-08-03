"""
Comprehensive Unit Test Suite for Observability & Developer Dashboard Subsystem.
"""

import pytest
import time
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.metric import Metric, MetricType
from app.models.trace import TraceSpan, SpanStatus
from app.models.health_status import SubsystemHealth, HealthState
from app.models.timeline_event import TimelineEvent
from app.observability.metrics_service import MetricsService
from app.observability.trace_manager import TraceManager
from app.observability.log_aggregator import LogAggregator
from app.observability.health_monitor import HealthMonitor
from app.observability.performance_profiler import PerformanceProfiler
from app.observability.event_timeline import EventTimeline
from app.observability.workflow_visualizer import WorkflowVisualizer
from app.observability.dashboard_service import DashboardService
from app.api.dashboard_api import router as dashboard_router, set_dashboard_service


class TestMetricCollection:
    """Tests metrics recording, counters, gauges, histograms, and alerts."""

    def test_record_counter_and_gauge(self):
        service = MetricsService()
        service.record_counter("test_counter", 5.0)
        service.record_gauge("test_gauge", 42.0, unit="MB")

        summary = service.get_summary()
        assert summary["counters"]["test_counter"] == 5.0
        assert summary["gauges"]["test_gauge"] == 42.0

    def test_record_latency_histogram(self):
        service = MetricsService()
        service.record_latency("op_latency", 100.0)
        service.record_latency("op_latency", 300.0)

        summary = service.get_summary()
        hist = summary["histograms"]["op_latency"]
        assert hist["count"] == 2
        assert hist["avg"] == 200.0
        assert hist["max"] == 300.0
        assert hist["min"] == 100.0

    def test_helpers_recording(self):
        service = MetricsService()
        service.record_llm_latency(250.0, model="gpt-4o")
        service.record_token_usage(prompt_tokens=100, completion_tokens=50)
        service.record_memory_retrieval(duration_ms=45.0, results_count=5)
        service.record_knowledge_retrieval(duration_ms=80.0, hits=3)
        service.record_tool_latency("search_tool", 120.0, success=True)
        service.record_plugin_latency("my_plugin", 30.0)
        service.record_workflow_duration("wf-1", 1500.0, success=True)
        service.record_retry_count("web_scrape", 2)

        summary = service.get_summary()
        assert "llm_latency_ms" in summary["histograms"]
        assert summary["counters"]["llm_total_tokens"] == 150.0
        assert summary["counters"]["memory_retrieval_count"] == 1.0

    def test_high_latency_alert_callback(self):
        alert_mock = MagicMock()
        service = MetricsService(high_latency_threshold_ms=500.0)
        service.register_alert_callback(alert_mock)

        service.record_latency("fast_op", 100.0)
        alert_mock.assert_not_called()

        service.record_latency("slow_op", 1000.0)
        alert_mock.assert_called_once_with("slow_op", 1000.0)


class TestTraceGeneration:
    """Tests distributed trace creation, spans, context managers, and hierarchy."""

    def test_trace_span_lifecycle(self):
        tm = TraceManager()
        root_span = tm.start_trace("root_workflow")
        assert root_span.trace_id.startswith("trace-")
        assert root_span.operation_name == "root_workflow"

        child_span = tm.start_span(
            trace_id=root_span.trace_id,
            operation_name="child_task",
            parent_span_id=root_span.span_id
        )

        assert child_span.parent_span_id == root_span.span_id
        tm.finish_span(child_span, status=SpanStatus.OK)
        tm.finish_span(root_span, status=SpanStatus.OK)

        spans = tm.get_trace_spans(root_span.trace_id)
        assert len(spans) == 2

    def test_sync_and_async_span_context_managers(self):
        tm = TraceManager()
        trace_id = tm.generate_trace_id()

        with tm.span(trace_id, "sync_operation") as span:
            assert span.operation_name == "sync_operation"

        spans = tm.get_trace_spans(trace_id)
        assert len(spans) == 1
        assert spans[0].status == SpanStatus.OK

    @pytest.mark.asyncio
    async def test_async_span_context_manager(self):
        tm = TraceManager()
        trace_id = tm.generate_trace_id()

        async with tm.async_span(trace_id, "async_operation") as span:
            assert span.operation_name == "async_operation"

        spans = tm.get_trace_spans(trace_id)
        assert len(spans) == 1
        assert spans[0].status == SpanStatus.OK


class TestHealthMonitoring:
    """Tests health probes, status calculation, and missing subsystem reporting."""

    def test_default_core_subsystems_healthy(self):
        hm = HealthMonitor()
        statuses = hm.check_all()
        assert len(statuses) >= 8
        assert "Voice" in statuses
        assert "Memory" in statuses
        assert hm.get_overall_system_status() == HealthState.HEALTHY

    def test_missing_subsystem_reporting(self):
        hm = HealthMonitor()
        missing_health = hm.report_missing_subsystem("UnknownSubsystem", "Module not found.")
        assert missing_health.state == HealthState.UNHEALTHY
        assert hm.get_overall_system_status() == HealthState.UNHEALTHY

    def test_custom_subsystem_probe(self):
        hm = HealthMonitor()
        probe_fn = MagicMock(return_value=SubsystemHealth(
            subsystem_name="CustomEngine",
            state=HealthState.DEGRADED,
            details="Slow response"
        ))
        hm.register_subsystem_probe("CustomEngine", probe_fn)

        health = hm.check_subsystem("CustomEngine")
        assert health.state == HealthState.DEGRADED
        probe_fn.assert_called_once()


class TestLogAggregation:
    """Tests structured log entry creation, filtering, tailing, and querying."""

    def test_logging_and_tailing(self):
        logger = LogAggregator()
        logger.info("System initialized", subsystem="core")
        logger.warning("Memory usage elevated", subsystem="memory")
        logger.error("Failed to connect to API", subsystem="llm")

        logs = logger.tail(10)
        assert len(logs) == 3
        assert logger.get_error_count() == 1

    def test_query_filtering(self):
        logger = LogAggregator()
        logger.info("Start task", subsystem="planner", trace_id="trace-100")
        logger.error("Task crashed", subsystem="planner", trace_id="trace-100")
        logger.info("Other message", subsystem="voice", trace_id="trace-200")

        trace_logs = logger.query(trace_id="trace-100")
        assert len(trace_logs) == 2

        error_logs = logger.query(level="ERROR")
        assert len(error_logs) == 1
        assert error_logs[0]["subsystem"] == "planner"


class TestTimelineOrdering:
    """Tests timeline event ordering and trace filtering."""

    def test_timeline_ordering(self):
        timeline = EventTimeline()
        timeline.record_event("trace-1", "Planner", "Step 1 started")
        timeline.record_event("trace-1", "Browser", "Step 2 searching web")
        timeline.record_event("trace-2", "Voice", "Voice prompt received")

        events_t1 = timeline.get_timeline_for_trace("trace-1")
        assert len(events_t1) == 2
        assert events_t1[0]["message"] == "Step 1 started"
        assert events_t1[1]["message"] == "Step 2 searching web"


class TestWorkflowVisualizer:
    """Tests workflow DAG graph and agent topology generation."""

    def test_generate_workflow_dag(self):
        tm = TraceManager()
        trace_id = tm.generate_trace_id()
        root = tm.start_span(trace_id, "planner")
        child = tm.start_span(trace_id, "browser_search", parent_span_id=root.span_id)
        tm.finish_span(child)
        tm.finish_span(root)

        spans = tm.get_trace_spans(trace_id)
        visualizer = WorkflowVisualizer()
        dag = visualizer.generate_workflow_dag(spans)

        assert dag["total_nodes"] == 2
        assert len(dag["edges"]) >= 1
        assert dag["root_id"] == root.span_id

    def test_generate_live_agent_graph(self):
        visualizer = WorkflowVisualizer()
        agents = [
            {"name": "Planner Agent", "target": "Research Agent", "status": "running"},
            {"name": "Research Agent", "target": "Browser Agent", "status": "running"}
        ]
        graph = visualizer.generate_live_agent_graph(agents)
        assert graph["active_count"] == 3
        assert len(graph["edges"]) == 2


class TestPerformanceProfiler:
    """Tests P50/P95/P99 calculations and automated recommendations."""

    def test_percentile_calculations(self):
        profiler = PerformanceProfiler()
        latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        stats = profiler.calculate_percentiles(latencies)

        assert stats["p50"] == 50.0
        assert stats["p95"] == 100.0
        assert stats["p99"] == 100.0
        assert stats["avg"] == 55.0

    def test_automated_recommendation_generation(self):
        metrics = MetricsService()
        metrics.record_memory_retrieval(600.0, results_count=1)
        metrics.record_retry_count("op", 5)

        profiler = PerformanceProfiler(metrics_service=metrics)
        recommendations = profiler.generate_recommendations()

        assert len(recommendations) >= 2
        categories = [r["category"] for r in recommendations]
        assert "Memory & Search" in categories
        assert "Execution Runtime" in categories


class TestDashboardAPI:
    """Tests FastAPI router endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(dashboard_router)
        self.dashboard_service = DashboardService()
        set_dashboard_service(self.dashboard_service)
        self.client = TestClient(self.app)

    def test_dashboard_summary_endpoint(self):
        res = self.client.get("/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert "system" in data
        assert "summary_cards" in data

    def test_metrics_endpoint(self):
        res = self.client.get("/metrics")
        assert res.status_code == 200
        assert "counters" in res.json()

    def test_health_endpoint(self):
        res = self.client.get("/health")
        assert res.status_code == 200
        assert "Voice" in res.json()

    def test_logs_endpoint(self):
        self.dashboard_service.log_aggregator.info("Test API log", subsystem="api")
        res = self.client.get("/logs?subsystem=api")
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_dashboard_html_render(self):
        res = self.client.get("/dashboard")
        assert res.status_code == 200
        assert "ASTRA OS" in res.text
