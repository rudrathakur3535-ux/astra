"""
Execution State Model for Project Astra.
Encapsulates workflow status, completed steps, progress percentage, and timestamps.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionState:
    """
    Tracks state, status, progress, and step history of a workflow execution.
    """
    workflow_id: str
    goal_description: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    total_steps: int = 0
    completed_steps: int = 0
    current_step_id: Optional[str] = None
    completed_step_ids: List[str] = field(default_factory=list)
    failed_step_ids: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def progress_percentage(self) -> float:
        if self.total_steps == 0:
            return 0.0
        pct = (self.completed_steps / self.total_steps) * 100.0
        return min(round(pct, 1), 100.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "goal_description": self.goal_description,
            "status": self.status.value if isinstance(self.status, ExecutionStatus) else self.status,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "progress_percentage": self.progress_percentage,
            "current_step_id": self.current_step_id,
            "completed_step_ids": self.completed_step_ids,
            "failed_step_ids": self.failed_step_ids,
            "error_message": self.error_message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata
        }
