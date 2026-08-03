"""
Workflow Model for Project Astra.
Represents multi-agent DAG execution workflows.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import time
import uuid

from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult


class WorkflowMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Workflow:
    """
    Represents a multi-agent workflow graph with task nodes and execution logs.
    """
    name: str
    goal_description: str
    tasks: List[AgentTask] = field(default_factory=list)
    mode: WorkflowMode = WorkflowMode.HYBRID
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: WorkflowStatus = WorkflowStatus.PENDING
    results: Dict[str, AgentResult] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def add_log(self, message: str) -> None:
        timestamp_str = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp_str}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "goal_description": self.goal_description,
            "mode": self.mode.value if isinstance(self.mode, WorkflowMode) else self.mode,
            "status": self.status.value if isinstance(self.status, WorkflowStatus) else self.status,
            "tasks": [t.to_dict() for t in self.tasks],
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "logs": self.logs,
            "created_at": self.created_at
        }
