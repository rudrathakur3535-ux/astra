"""
Personal Knowledge Graph Node Model for Project Astra OS.
Represents entity nodes (Projects, Skills, Goals, Memories).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class KnowledgeNode:
    node_id: str
    label: str
    node_type: str  # project, skill, goal, memory, preference
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "node_type": self.node_type,
            "properties": self.properties,
            "created_at": self.created_at
        }
