"""
Runtime Event Model for Project Astra.
Defines execution events broadcast by the Autonomous Execution Runtime.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class RuntimeEventType(str, Enum):
    WORKFLOW_STARTED = "workflow_started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    CHECKPOINT_SAVED = "checkpoint_saved"
    STEP_RETRIED = "step_retried"
    STEP_TIMEOUT = "step_timeout"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


@dataclass
class RuntimeEvent:
    """
    Event payload emitted during runtime execution.
    """
    event_type: RuntimeEventType
    workflow_id: str
    step_id: Optional[str] = None
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value if isinstance(self.event_type, RuntimeEventType) else self.event_type,
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "message": self.message,
            "payload": self.payload,
            "timestamp": self.timestamp
        }
