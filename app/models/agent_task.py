"""
Agent Task Model for Project Astra.
Represents an atomic task assigned to a specialist agent within a multi-agent workflow.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import uuid


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentTask:
    """
    Task definition assigned to a specialist agent.
    """
    description: str
    target_agent_type: str = "general"
    input_data: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: List[str] = field(default_factory=list)  # List of prerequisite task IDs
    max_retries: int = 2
    timeout_seconds: float = 30.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "target_agent_type": self.target_agent_type,
            "input_data": self.input_data,
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            "dependencies": self.dependencies,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at
        }
