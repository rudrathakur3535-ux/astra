"""
User Habit Model for Project Astra OS.
Represents detected user routines, action sequences, trigger contexts, and confidence scores.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class Habit:
    habit_id: str
    name: str
    trigger_context: str
    action_sequence: List[str]
    occurrences: int = 1
    confidence_score: float = 0.5
    created_at: float = field(default_factory=time.time)
    last_triggered: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "habit_id": self.habit_id,
            "name": self.name,
            "trigger_context": self.trigger_context,
            "action_sequence": self.action_sequence,
            "occurrences": self.occurrences,
            "confidence_score": round(self.confidence_score, 2),
            "created_at": self.created_at,
            "last_triggered": self.last_triggered
        }
