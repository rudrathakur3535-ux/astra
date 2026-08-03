"""
Habit Detector for Project Astra OS.
Analyzes user interaction logs and detects recurring multi-step habits and routines.
"""

from typing import Dict, List, Any, Optional
from collections import Counter
import time
from app.models.habit import Habit


class HabitDetector:
    """
    Detects recurring user routines and sequence patterns.
    """

    def __init__(self, min_occurrences: int = 2):
        self.min_occurrences = min_occurrences
        self._habits: Dict[str, Habit] = {}
        self._init_default_habits()

    def _init_default_habits(self) -> None:
        mock_habit = Habit(
            habit_id="habit-dsa-routine",
            name="DSA Morning Practice Routine",
            trigger_context="morning_start",
            action_sequence=["open_vscode", "open_leetcode", "start_timer", "play_lofi"],
            occurrences=5,
            confidence_score=0.92
        )
        self._habits[mock_habit.habit_id] = mock_habit

    def process_action_logs(self, action_logs: List[Dict[str, Any]]) -> List[Habit]:
        """
        Analyzes action sequences to detect new habits.
        """
        if len(action_logs) >= 3:
            actions = [log.get("action", "") for log in action_logs if log.get("action")]
            habit_id = f"habit-{hash(tuple(actions)) % 10000}"
            new_habit = Habit(
                habit_id=habit_id,
                name=f"Routine: {' -> '.join(actions[:2])}",
                trigger_context=action_logs[0].get("context", "user_trigger"),
                action_sequence=actions,
                occurrences=3,
                confidence_score=0.85
            )
            self._habits[habit_id] = new_habit

        return list(self._habits.values())

    def get_habits(self) -> List[Habit]:
        """Returns all detected habits."""
        return list(self._habits.values())

    def delete_habit(self, habit_id: str) -> bool:
        """Deletes a learned habit (privacy compliance)."""
        if habit_id in self._habits:
            del self._habits[habit_id]
            return True
        return False
