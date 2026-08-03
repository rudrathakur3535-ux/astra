"""
Preference Engine for Project Astra OS.
Learns developer preferences for AI LLM providers, tools, themes, and modes.
"""

from typing import Dict, Any, Optional


class PreferenceEngine:
    """
    User Preference Adaptor.
    """

    def __init__(self):
        self._preferences: Dict[str, Any] = {
            "default_llm_provider": "gemini",
            "theme": "dark_glassmorphism",
            "auto_code_review": True,
            "browser_headless": False
        }

    def get_preference(self, key: str, default_val: Any = None) -> Any:
        return self._preferences.get(key, default_val)

    def set_preference(self, key: str, value: Any) -> None:
        self._preferences[key] = value

    def get_all_preferences(self) -> Dict[str, Any]:
        return dict(self._preferences)

    def reset_preferences(self) -> None:
        self._preferences.clear()
