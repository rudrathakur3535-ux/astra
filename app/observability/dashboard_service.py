"""
Master Dashboard Service for Project Astra OS.
Aggregates metrics, traces, health status, logs, timeline, and workflow graphs into dashboard payloads.
"""

from typing import Dict, List, Any, Optional
from app.observability.metrics_service import MetricsService
from app.observability.trace_manager import TraceManager
from app.observability.log_aggregator import LogAggregator
from app.observability.health_monitor import HealthMonitor
from app.observability.performance_profiler import PerformanceProfiler
from app.observability.event_timeline import EventTimeline
from app.observability.workflow_visualizer import WorkflowVisualizer


class DashboardService:
    """
    Unified Dashboard Aggregator Service.
    """

    def __init__(
        self,
        metrics_service: Optional[MetricsService] = None,
        trace_manager: Optional[TraceManager] = None,
        log_aggregator: Optional[LogAggregator] = None,
        health_monitor: Optional[HealthMonitor] = None,
        performance_profiler: Optional[PerformanceProfiler] = None,
        event_timeline: Optional[EventTimeline] = None,
        workflow_visualizer: Optional[WorkflowVisualizer] = None
    ):
        self.metrics_service = metrics_service or MetricsService()
        self.trace_manager = trace_manager or TraceManager()
        self.log_aggregator = log_aggregator or LogAggregator()
        self.health_monitor = health_monitor or HealthMonitor()
        self.performance_profiler = performance_profiler or PerformanceProfiler(metrics_service=self.metrics_service)
        self.event_timeline = event_timeline or EventTimeline()
        self.workflow_visualizer = workflow_visualizer or WorkflowVisualizer()

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Returns a complete system overview dictionary for the developer dashboard.
        """
        health_report = self.health_monitor.check_all()
        overall_health = self.health_monitor.get_overall_system_status().value
        metrics_summary = self.metrics_service.get_summary()
        all_traces = self.trace_manager.get_all_traces()
        active_trace_count = self.trace_manager.get_active_trace_count()
        recent_logs = self.log_aggregator.tail(20)
        recent_events = self.event_timeline.get_recent_events(20)
        profiler_data = self.performance_profiler.get_profiler_stats()
        agent_graph = self.workflow_visualizer.generate_live_agent_graph([])

        return {
            "system": {
                "name": "Astra OS Developer Dashboard",
                "status": overall_health,
                "subsystems": health_report
            },
            "summary_cards": {
                "running_workflows": active_trace_count,
                "active_agents": agent_graph.get("active_count", 0),
                "total_traces": len(all_traces),
                "total_logs": len(recent_logs),
                "error_count": self.log_aggregator.get_error_count(),
                "total_metrics": metrics_summary.get("total_metrics_recorded", 0)
            },
            "metrics": metrics_summary,
            "traces": all_traces,
            "timeline": recent_events,
            "logs": recent_logs,
            "agent_graph": agent_graph,
            "recommendations": profiler_data.get("recommendations", [])
        }
