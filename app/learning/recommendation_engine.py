"""
Recommendation Engine for Project Astra OS.
Ranks and generates proactive workflow suggestions based on learned habits.
"""

from typing import Dict, List, Any, Optional
from app.models.recommendation import Recommendation
from app.models.habit import Habit


class RecommendationEngine:
    """
    Proactive Recommendation & Ranking Engine.
    """

    def __init__(self):
        self._recommendations: Dict[str, Recommendation] = {}
        self._init_default_recommendations()

    def _init_default_recommendations(self) -> None:
        rec = Recommendation(
            recommendation_id="rec-dsa-routine",
            title="Automate DSA Morning Setup?",
            description="You frequently open VS Code, LeetCode, and Spotify between 09:00 - 10:00 AM. Would you like Astra to prepare this workflow automatically?",
            suggested_action={"workflow": "habit-dsa-routine"},
            score=0.95
        )
        self._recommendations[rec.recommendation_id] = rec

    def generate_recommendations_from_habits(self, habits: List[Habit]) -> List[Recommendation]:
        for habit in habits:
            if habit.confidence_score >= 0.8:
                rec_id = f"rec-{habit.habit_id}"
                rec = Recommendation(
                    recommendation_id=rec_id,
                    title=f"Automate '{habit.name}'?",
                    description=f"Detected sequence '{' -> '.join(habit.action_sequence[:3])}'. Automate routine?",
                    suggested_action={"action_sequence": habit.action_sequence},
                    score=habit.confidence_score
                )
                self._recommendations[rec_id] = rec
        return list(self._recommendations.values())

    def get_pending_recommendations(self) -> List[Recommendation]:
        return [r for r in self._recommendations.values() if r.status == "pending"]

    def accept_recommendation(self, rec_id: str) -> bool:
        if rec_id in self._recommendations:
            self._recommendations[rec_id].status = "accepted"
            return True
        return False
