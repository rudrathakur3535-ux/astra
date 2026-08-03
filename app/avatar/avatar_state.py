"""
Avatar State Model for Project Astra OS (v2.1 Specification).
Represents the complete visual and animation state of the Astra character at any moment.
Pushed to frontend renderers via WebSocket.
"""

from dataclasses import dataclass, field, asdict
from typing import Tuple, Dict, Any
import time

from app.avatar.avatar_enums import (
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
)


@dataclass
class AvatarState:
    """
    Complete snapshot of Astra's character state for v2.1.
    """

    # Primary visual states
    emotion: AstraEmotion = AstraEmotion.NEUTRAL
    emotion_strength: float = 0.50  # 0.0 to 1.0 intensity scale
    outfit_mode: AstraOutfit = AstraOutfit.RELAX
    gesture: AstraGesture = AstraGesture.NONE
    gesture_priority: AstraGesturePriority = AstraGesturePriority.NORMAL
    gesture_duration: float = 1.5  # Duration in seconds

    # Eye tracking & Focus
    eye_focus: AstraEyeFocus = AstraEyeFocus.USER
    eye_target_x: float = 0.50
    eye_target_y: float = 0.50

    # Speech & Voice metadata
    speech_style: Dict[str, float] = field(
        default_factory=lambda: {
            "speed": 1.0,
            "pitch": 0.95,
            "energy": 0.75,
            "pause_level": 0.30,
        }
    )
    is_speaking: bool = False
    is_listening: bool = False
    is_thinking: bool = False
    mouth_openness: float = 0.0

    # Orchestration & Routing metadata (Backend only)
    tool_status: Dict[str, Any] = field(
        default_factory=lambda: {"requires_tool": False, "tool": "none"}
    )
    reasoning_hint: str = ""

    # Timestamp & Text
    last_updated: float = field(default_factory=time.time)
    reply_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-safe dictionary for WebSocket / REST transmission."""
        return {
            "emotion": self.emotion.value,
            "emotion_strength": round(max(0.0, min(1.0, self.emotion_strength)), 2),
            "outfit_mode": self.outfit_mode.value,
            "gesture": self.gesture.value,
            "gesture_priority": self.gesture_priority.value,
            "gesture_duration": round(max(0.1, self.gesture_duration), 2),
            "eye_focus": self.eye_focus.value,
            "eye_target_x": round(self.eye_target_x, 4),
            "eye_target_y": round(self.eye_target_y, 4),
            "speech_style": self.speech_style,
            "is_speaking": self.is_speaking,
            "is_listening": self.is_listening,
            "is_thinking": self.is_thinking,
            "mouth_openness": round(self.mouth_openness, 3),
            "tool_status": self.tool_status,
            "reasoning_hint": self.reasoning_hint,
            "last_updated": self.last_updated,
            "reply_text": self.reply_text,
        }

    def copy(self) -> "AvatarState":
        """Create a shallow copy of this state."""
        return AvatarState(
            emotion=self.emotion,
            emotion_strength=self.emotion_strength,
            outfit_mode=self.outfit_mode,
            gesture=self.gesture,
            gesture_priority=self.gesture_priority,
            gesture_duration=self.gesture_duration,
            eye_focus=self.eye_focus,
            eye_target_x=self.eye_target_x,
            eye_target_y=self.eye_target_y,
            speech_style=dict(self.speech_style),
            is_speaking=self.is_speaking,
            is_listening=self.is_listening,
            is_thinking=self.is_thinking,
            mouth_openness=self.mouth_openness,
            tool_status=dict(self.tool_status),
            reasoning_hint=self.reasoning_hint,
            last_updated=self.last_updated,
            reply_text=self.reply_text,
        )
