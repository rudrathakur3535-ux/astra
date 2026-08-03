"""
Agent Result Model for Project Astra.
Standardized output payload returned by specialist agent executions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time


@dataclass
class AgentResult:
    """
    Standardized result payload returned by an agent upon completing a task.
    """
    task_id: str
    agent_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    retry_count: int = 0
    artifacts: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "retry_count": self.retry_count,
            "artifacts": self.artifacts,
            "timestamp": self.timestamp
        }
