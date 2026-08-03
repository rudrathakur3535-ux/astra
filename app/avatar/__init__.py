"""
Avatar Package for Project Astra OS (v2.1 Enterprise Specification).
Provides character state management, LLM response parsing, animation state enums,
and metadata validation for the interactive animated Astra companion.
"""

from app.avatar.avatar_enums import (
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
)
from app.avatar.avatar_state import AvatarState
from app.avatar.avatar_state_manager import AvatarStateManager, avatar_state_manager
from app.avatar.response_parser import parse_llm_response

__all__ = [
    "AstraEmotion",
    "AstraOutfit",
    "AstraGesture",
    "AstraEyeFocus",
    "AstraGesturePriority",
    "AvatarState",
    "AvatarStateManager",
    "avatar_state_manager",
    "parse_llm_response",
]
