"""
Agent Metrics Tracker Module for Project Astra.
Tracks execution latency, success rates, retry counts, most-used agents, and tool invocation stats.
"""

from typing import Dict, Any, List
import time
from app.models.agent_result import AgentResult
from app.utils.logger import logger


class AgentMetricsTracker:
    """
    Performance metrics collector and dashboard statistics builder.
    """

    def __init__(self):
        self._agent_stats: Dict[str, Dict[str, Any]] = {}
        self._total_tasks: int = 0
        self._successful_tasks: int = 0
        self._failed_tasks: int = 0

    def record_execution(self, result: AgentResult) -> None:
        """
        Records metrics from an agent execution result.
        """
        agent = result.agent_name
        if agent not in self._agent_stats:
            self._agent_stats[agent] = {
                "invocations": 0,
                "successes": 0,
                "failures": 0,
                "total_time_ms": 0.0,
                "total_retries": 0
            }

        stats = self._agent_stats[agent]
        stats["invocations"] += 1
        stats["total_time_ms"] += result.execution_time_ms
        stats["total_retries"] += result.retry_count

        self._total_tasks += 1
        if result.success:
            stats["successes"] += 1
            self._successful_tasks += 1
        else:
            stats["failures"] += 1
            self._failed_tasks += 1

        logger.debug(f"[MetricsTracker] Recorded metrics for '{agent}': time={result.execution_time_ms:.2f}ms success={result.success}")

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Generates comprehensive metrics summary for the developer dashboard.
        """
        overall_success_rate = (self._successful_tasks / self._total_tasks * 100.0) if self._total_tasks > 0 else 0.0

        most_used_agent = "None"
        max_invocations = 0
        agent_summaries = {}

        for agent, stats in self._agent_stats.items():
            inv = stats["invocations"]
            if inv > max_invocations:
                max_invocations = inv
                most_used_agent = agent

            avg_latency = (stats["total_time_ms"] / inv) if inv > 0 else 0.0
            success_rate = (stats["successes"] / inv * 100.0) if inv > 0 else 0.0

            agent_summaries[agent] = {
                "invocations": inv,
                "success_rate_percent": round(success_rate, 1),
                "avg_latency_ms": round(avg_latency, 2),
                "total_retries": stats["total_retries"]
            }

        return {
            "total_tasks_processed": self._total_tasks,
            "overall_success_rate_percent": round(overall_success_rate, 1),
            "most_used_agent": most_used_agent,
            "agent_performance": agent_summaries
        }


# Global default MetricsTracker singleton
metrics_tracker = AgentMetricsTracker()
