"""
Execution Monitor Module for Project Astra.
Collects and exposes real-time runtime metrics for live dashboard monitoring.
"""

from typing import Dict, Any, List
import time

from app.models.execution_state import ExecutionState, ExecutionStatus
from app.models.runtime_event import RuntimeEvent, RuntimeEventType
from app.utils.logger import logger


class ExecutionMonitor:
    """
    Live metrics monitor tracking runtime workflow performance.
    """

    def __init__(self):
        self.events: List[RuntimeEvent] = []
        self.total_workflows_executed = 0
        self.total_steps_executed = 0
        self.failed_steps_count = 0
        self.retried_steps_count = 0

    def record_event(self, event: RuntimeEvent) -> None:
        """Records a runtime execution event."""
        self.events.append(event)

        if event.event_type == RuntimeEventType.WORKFLOW_COMPLETED:
            self.total_workflows_executed += 1
        elif event.event_type == RuntimeEventType.STEP_COMPLETED:
            self.total_steps_executed += 1
        elif event.event_type == RuntimeEventType.STEP_FAILED:
            self.failed_steps_count += 1
        elif event.event_type == RuntimeEventType.STEP_RETRIED:
            self.retried_steps_count += 1

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Returns live dashboard runtime statistics.
        """
        failure_rate = (self.failed_steps_count / max(self.total_steps_executed, 1)) * 100.0
        return {
            "total_workflows_executed": self.total_workflows_executed,
            "total_steps_executed": self.total_steps_executed,
            "failed_steps_count": self.failed_steps_count,
            "retried_steps_count": self.retried_steps_count,
            "failure_rate_pct": round(failure_rate, 2),
            "recent_events_count": len(self.events)
        }
