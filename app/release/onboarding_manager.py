"""
User Onboarding & Workspace Initialization Manager for Project Astra OS.
Handles initial setup, provider selection wizard, and guided tutorial steps.
"""

from typing import Dict, List, Any, Optional
import time


class OnboardingManager:
    """
    Manages user onboarding flow and workspace initialization.
    """

    def __init__(self):
        self._onboarded = False
        self._user_profile: Dict[str, Any] = {}

    def is_onboarded(self) -> bool:
        """Returns True if user has completed initial onboarding."""
        return self._onboarded

    def complete_onboarding(self, username: str, primary_provider: str = "gemini", theme: str = "dark_glassmorphism") -> Dict[str, Any]:
        """Completes first-time onboarding setup."""
        self._user_profile = {
            "username": username,
            "primary_provider": primary_provider,
            "theme": theme,
            "completed_at": time.time()
        }
        self._onboarded = True
        return {
            "status": "onboarding_completed",
            "user_profile": self._user_profile,
            "next_steps": [
                "1. Try running a natural language prompt in Astra UI",
                "2. Explore the Observability Dashboard at http://localhost:8000/dashboard",
                "3. Enable GitHub / Gmail integrations",
                "4. Run a live E2E demo workflow"
            ]
        }
