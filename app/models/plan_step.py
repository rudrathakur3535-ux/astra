"""
Plan Step Model for Project Astra.
Represents an individual executable step in a multi-step task plan.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class PlanStep:
    """
    Individual step within an execution plan.
    """
    id: int
    tool: str
    args: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    expected_outcome: str = ""
    dependencies: List[int] = field(default_factory=list)  # Step IDs that must complete first
    fallback_tool: Optional[str] = None                    # Alternative tool if step fails
    fallback_args: Optional[Dict[str, Any]] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.tool,
            "args": self.args,
            "description": self.description,
            "expected_outcome": self.expected_outcome,
            "dependencies": self.dependencies,
            "fallback_tool": self.fallback_tool,
            "status": self.status.value if isinstance(self.status, StepStatus) else self.status,
            "result": self.result,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanStep":
        return cls(
            id=data.get("id", 1),
            tool=data.get("tool", ""),
            args=data.get("args", {}),
            description=data.get("description", ""),
            expected_outcome=data.get("expected_outcome", ""),
            dependencies=data.get("dependencies", []),
            fallback_tool=data.get("fallback_tool"),
            fallback_args=data.get("fallback_args"),
            status=StepStatus(data.get("status", "pending")),
            result=data.get("result"),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0)
        )
