"""
Execution Checkpoint Model for Project Astra.
Represents an immutable snapshot of workflow execution state after a step finishes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


@dataclass
class ExecutionCheckpoint:
    """
    State checkpoint saved to persistent store for crash recovery.
    """
    workflow_id: str
    step_id: str
    step_index: int
    step_result_data: Dict[str, Any] = field(default_factory=dict)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "step_index": self.step_index,
            "step_result_data": self.step_result_data,
            "context_snapshot": self.context_snapshot,
            "created_at": self.created_at
        }
