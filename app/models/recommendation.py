"""
Recommendation Model for Project Astra OS.
Represents proactive workflow suggestions and automated routine rankings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class Recommendation:
    recommendation_id: str
    title: str
    description: str
    suggested_action: Dict[str, Any]
    score: float = 0.85
    status: str = "pending"  # pending, accepted, dismissed
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "description": self.description,
            "suggested_action": self.suggested_action,
            "score": round(self.score, 2),
            "status": self.status,
            "created_at": self.created_at
        }
