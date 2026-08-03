"""
Learning Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.habit import Habit
from app.models.recommendation import Recommendation


class LearningPort(ABC):
    """
    Abstract Hexagonal Port interface for Learning & Adaptive Engine Adapters.
    """

    @abstractmethod
    def detect_habits(self, action_logs: List[Dict[str, Any]]) -> List[Habit]:
        """Analyzes logs and detects user habits."""
        pass

    @abstractmethod
    def generate_recommendations(self) -> List[Recommendation]:
        """Generates proactive workflow recommendations."""
        pass
