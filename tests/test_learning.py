"""
Comprehensive Unit & Integration Test Suite for Adaptive Intelligence & Learning Engine Platform.
"""

import pytest
import time
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.habit import Habit
from app.models.pattern import Pattern
from app.models.recommendation import Recommendation
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge

from app.learning.habit_detector import HabitDetector
from app.learning.pattern_miner import PatternMiner
from app.learning.preference_engine import PreferenceEngine
from app.learning.workflow_learner import WorkflowLearner
from app.learning.prompt_optimizer import PromptOptimizer
from app.learning.knowledge_graph import PersonalKnowledgeGraph
from app.learning.recommendation_engine import RecommendationEngine
from app.learning.feedback_analyzer import FeedbackAnalyzer

from app.services.learning_service import LearningService
from app.api.learning_api import router as learning_router


class TestHabitAndPatternDetection:
    """Tests Habit detection, pattern mining, and privacy deletion."""

    def test_habit_detector_processing(self):
        detector = HabitDetector()
        logs = [
            {"action": "open_vscode", "context": "morning"},
            {"action": "open_leetcode", "context": "morning"},
            {"action": "start_timer", "context": "morning"}
        ]
        habits = detector.process_action_logs(logs)
        assert len(habits) >= 2

        # Privacy habit deletion
        target_id = habits[0].habit_id
        assert detector.delete_habit(target_id) is True
        assert detector.delete_habit("invalid_id") is False

    def test_pattern_miner(self):
        miner = PatternMiner()
        patterns = miner.mine_patterns([])
        assert len(patterns) >= 1
        assert patterns[0].event_type == "git_pull_before_test"


class TestPreferencesAndFeedback:
    """Tests Preference Engine, Prompt Optimizer, and Feedback Analyzer."""

    def test_preference_engine(self):
        engine = PreferenceEngine()
        assert engine.get_preference("default_llm_provider") == "gemini"

        engine.set_preference("theme", "cyberpunk_dark")
        assert engine.get_preference("theme") == "cyberpunk_dark"

        engine.reset_preferences()
        assert len(engine.get_all_preferences()) == 0

    def test_feedback_analyzer(self):
        pref_engine = PreferenceEngine()
        analyzer = FeedbackAnalyzer(pref_engine)

        res = analyzer.analyze_feedback_signal("correction", "Please always use OpenAI for coding tasks.")
        assert res["status"] == "feedback_processed"
        assert pref_engine.get_preference("default_llm_provider") == "openai"

    def test_prompt_optimizer(self):
        optimizer = PromptOptimizer()
        optimizer.record_prompt_outcome("coding", "Base prompt", is_success=False)
        opt_prompt = optimizer.optimize_system_prompt("Base coding prompt", "coding")
        assert "Optimization Hint" in opt_prompt


class TestKnowledgeGraphAndRecommendations:
    """Tests Personal Knowledge Graph, Workflow Learner, and Recommendation Engine."""

    def test_personal_knowledge_graph(self):
        kg = PersonalKnowledgeGraph()
        summary = kg.get_graph_summary()
        assert summary["node_count"] >= 3
        assert summary["edge_count"] >= 2

        n_new = KnowledgeNode("n-goal", "Master AI Systems", "goal")
        kg.add_node(n_new)
        assert kg.get_graph_summary()["node_count"] == summary["node_count"] + 1

        kg.clear()
        assert kg.get_graph_summary()["node_count"] == 0

    def test_workflow_learner(self):
        learner = WorkflowLearner()
        habit = Habit("h-1", "Git Flow", "dev", ["git_pull", "pytest", "vscode"])
        wf = learner.learn_workflow_from_habit(habit)
        assert wf["auto_generated"] is True
        assert len(wf["steps"]) == 3

    def test_recommendation_engine(self):
        engine = RecommendationEngine()
        pending = engine.get_pending_recommendations()
        assert len(pending) >= 1

        rec_id = pending[0].recommendation_id
        assert engine.accept_recommendation(rec_id) is True
        assert pending[0].status == "accepted"


class TestMasterLearningService:
    """Tests master learning service and full privacy reset."""

    def test_master_learning_and_reset(self):
        svc = LearningService()
        res_learn = svc.record_user_actions_and_learn([
            {"action": "git_status"},
            {"action": "git_pull"},
            {"action": "pytest"}
        ])
        assert res_learn["detected_habits_count"] >= 1

        # Full Privacy Reset
        reset_res = svc.reset_all_learning_data()
        assert reset_res["status"] == "learning_reset_complete"
        assert len(svc.habit_detector.get_habits()) == 0


class TestLearningAPIEndpoints:
    """Tests FastAPI Learning Router REST endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(learning_router)
        self.client = TestClient(self.app)

    def test_habits_endpoints(self):
        res = self.client.get("/api/learning/habits")
        assert res.status_code == 200
        habits = res.json()["habits"]
        assert len(habits) >= 1

        habit_id = habits[0]["habit_id"]
        res_del = self.client.delete(f"/api/learning/habits/{habit_id}")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "deleted"

    def test_preferences_endpoints(self):
        res_get = self.client.get("/api/learning/preferences")
        assert res_get.status_code == 200

        res_upd = self.client.post("/api/learning/preferences", json={"key": "theme", "value": "glass_dark"})
        assert res_upd.status_code == 200
        assert res_upd.json()["value"] == "glass_dark"

    def test_recommendations_endpoints(self):
        res_get = self.client.get("/api/learning/recommendations")
        assert res_get.status_code == 200
        recs = res_get.json()["recommendations"]
        assert len(recs) >= 1

        rec_id = recs[0]["recommendation_id"]
        res_acc = self.client.post("/api/learning/recommendations/accept", json={"recommendation_id": rec_id})
        assert res_acc.status_code == 200
        assert res_acc.json()["status"] == "accepted"

    def test_knowledge_graph_endpoint(self):
        res = self.client.get("/api/learning/knowledge-graph")
        assert res.status_code == 200
        assert "node_count" in res.json()

    def test_feedback_and_reset_endpoints(self):
        res_fb = self.client.post("/api/learning/feedback", json={
            "feedback_type": "preference",
            "message": "Prefer Gemini provider"
        })
        assert res_fb.status_code == 200
        assert res_fb.json()["status"] == "feedback_processed"

        res_reset = self.client.post("/api/learning/reset")
        assert res_reset.status_code == 200
        assert res_reset.json()["status"] == "learning_reset_complete"
