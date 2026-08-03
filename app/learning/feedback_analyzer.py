"""
Feedback Analyzer for Project Astra OS.
Evaluates user corrections, feedback signals, and explicit instructions.
"""

from typing import Dict, List, Any, Optional
from app.learning.preference_engine import PreferenceEngine


class FeedbackAnalyzer:
    """
    User Feedback & Correction Signal Analyzer.
    """

    def __init__(self, preference_engine: PreferenceEngine):
        self.preference_engine = preference_engine

    def analyze_feedback_signal(self, feedback_type: str, message: str) -> Dict[str, Any]:
        """
        Processes feedback (e.g. "always use gemini", "prefer dark mode") and updates preferences.
        """
        msg_lower = message.lower()
        adapted_key = None

        if "gemini" in msg_lower:
            self.preference_engine.set_preference("default_llm_provider", "gemini")
            adapted_key = "default_llm_provider"
        elif "openai" in msg_lower or "gpt" in msg_lower:
            self.preference_engine.set_preference("default_llm_provider", "openai")
            adapted_key = "default_llm_provider"

        return {
            "status": "feedback_processed",
            "feedback_type": feedback_type,
            "adapted_preference_key": adapted_key,
            "current_preferences": self.preference_engine.get_all_preferences()
        }
