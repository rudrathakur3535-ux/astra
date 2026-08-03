"""
Goal Model for Project Astra.
Encapsulates user intent and goal metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


@dataclass
class Goal:
    """
    Represents a high-level user goal passed to Astra's planning engine.
    """
    description: str
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "context": self.context,
            "timestamp": self.timestamp
        }
