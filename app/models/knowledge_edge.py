"""
Personal Knowledge Graph Edge Model for Project Astra OS.
Represents relationships and weights between entity nodes.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class KnowledgeEdge:
    edge_id: str
    source_id: str
    target_id: str
    relation_type: str  # HAS_SKILL, USES_PROJECT, PREFERS, RELATED_TO
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "weight": round(self.weight, 2),
            "created_at": self.created_at
        }
