"""
Master Learning & Adaptive Service for Project Astra OS.
Orchestrates habit detection, preference learning, knowledge graph management, and recommendations.
"""

from typing import Dict, List, Any, Optional
from app.learning.habit_detector import HabitDetector
from app.learning.pattern_miner import PatternMiner
from app.learning.preference_engine import PreferenceEngine
from app.learning.workflow_learner import WorkflowLearner
from app.learning.prompt_optimizer import PromptOptimizer
from app.learning.knowledge_graph import PersonalKnowledgeGraph
from app.learning.recommendation_engine import RecommendationEngine
from app.learning.feedback_analyzer import FeedbackAnalyzer


class LearningService:
    """
    Master Adaptive Intelligence Subsystem Orchestrator.
    """

    def __init__(self):
        self.habit_detector = HabitDetector()
        self.pattern_miner = PatternMiner()
        self.preference_engine = PreferenceEngine()
        self.workflow_learner = WorkflowLearner()
        self.prompt_optimizer = PromptOptimizer()
        self.knowledge_graph = PersonalKnowledgeGraph()
        self.recommendation_engine = RecommendationEngine()
        self.feedback_analyzer = FeedbackAnalyzer(self.preference_engine)

    def record_user_actions_and_learn(self, action_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes user action logs to detect habits and update recommendations.
        """
        habits = self.habit_detector.process_action_logs(action_logs)
        recs = self.recommendation_engine.generate_recommendations_from_habits(habits)

        return {
            "detected_habits_count": len(habits),
            "recommendations_count": len(recs),
            "habits": [h.to_dict() for h in habits]
        }

    def reset_all_learning_data(self) -> Dict[str, Any]:
        """
        Full Privacy Reset: Wipes all learned habits, preferences, and knowledge graph edges.
        """
        self.habit_detector._habits.clear()
        self.preference_engine.reset_preferences()
        self.knowledge_graph.clear()
        self.recommendation_engine._recommendations.clear()

        return {
            "status": "learning_reset_complete",
            "message": "All learned habits, preferences, and personal knowledge graph nodes have been erased."
        }
