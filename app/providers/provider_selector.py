"""
Smart Provider Selector for Project Astra OS.
Selects optimal AI provider based on network availability, latency, privacy policies, and task requirements.
"""

from typing import Dict, Any, Optional
from app.providers.provider_router import ProviderRouter
from app.models.provider_status import ProviderState


class ProviderSelector:
    """
    Intelligent Provider Selection Engine.
    """

    def __init__(self, provider_router: Optional[ProviderRouter] = None):
        self.router = provider_router or ProviderRouter()

    def select_provider(
        self,
        task_type: str = "general",
        requires_privacy: bool = False,
        is_online: bool = True,
        user_preference: Optional[str] = None
    ) -> str:
        """
        Selects the best provider name based on rules:
        1. If user explicitly specified preference -> return user_preference
        2. If internet offline or privacy required -> "ollama" (local)
        3. If task is "fast_answer" -> "gemini"
        4. If task is "deep_reasoning" -> "openai"
        5. Default -> "openai" or "ollama" fallback
        """
        if user_preference and user_preference.lower() in self.router.list_providers():
            return user_preference.lower()

        if not is_online or requires_privacy:
            return "ollama"

        if task_type == "fast_answer":
            return "gemini"
        elif task_type == "deep_reasoning":
            return "openai"

        return "openai"
