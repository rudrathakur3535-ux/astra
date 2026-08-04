from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ExpressionEnum(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SMILE = "smile"
    EXCITED = "excited"
    THINKING = "thinking"
    CONFUSED = "confused"
    SURPRISED = "surprised"
    ANGRY = "angry"
    SAD = "sad"
    WORRIED = "worried"

class GestureEnum(str, Enum):
    NONE = "none"
    WAVE = "wave"
    EXPLAIN = "explain"
    POINT = "point"
    THUMBS_UP = "thumbs_up"
    THINKING = "thinking"

class PhonemeViseme(BaseModel):
    viseme: str = "mouth_closed"
    duration_ms: float = 100.0

class AvatarState(BaseModel):
    expression: Any = ExpressionEnum.NEUTRAL
    gesture: Any = GestureEnum.NONE
    emotion_strength: float = 0.50
    outfit_mode: Any = "relax"
    gesture_priority: Any = "normal"
    gesture_duration: float = 1.5
    eye_focus: Any = "user"
    reply_text: str = ""
    speech_style: Dict[str, float] = Field(default_factory=lambda: {"speed": 1.0, "pitch": 1.0, "energy": 0.5, "pause_level": 0.0})
    tool_status: Dict[str, Any] = Field(default_factory=lambda: {"requires_tool": False, "tool": None})
    reasoning_hint: str = ""
    viseme: str = "mouth_closed"
    is_speaking: bool = False
    is_listening: bool = False
    is_thinking: bool = False
    eye_blink: bool = False
    head_rotation_deg: float = 0.0
    joint_angles: Dict[str, float] = Field(default_factory=dict)
    active_layers: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        if "emotion" in data and "expression" not in data:
            data["expression"] = data.pop("emotion")
        super().__init__(**data)

    @property
    def emotion(self):
        return self.expression

    @emotion.setter
    def emotion(self, value):
        self.expression = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expression": self.expression.value if hasattr(self.expression, 'value') else str(self.expression),
            "emotion": self.expression.value if hasattr(self.expression, 'value') else str(self.expression),
            "emotion_strength": self.emotion_strength,
            "outfit_mode": self.outfit_mode.value if hasattr(self.outfit_mode, 'value') else str(self.outfit_mode),
            "gesture": self.gesture.value if hasattr(self.gesture, 'value') else str(self.gesture),
            "gesture_priority": self.gesture_priority.value if hasattr(self.gesture_priority, 'value') else str(self.gesture_priority),
            "gesture_duration": self.gesture_duration,
            "eye_focus": self.eye_focus.value if hasattr(self.eye_focus, 'value') else str(self.eye_focus),
            "reply_text": self.reply_text,
            "speech_style": self.speech_style,
            "tool_status": self.tool_status,
            "reasoning_hint": self.reasoning_hint,
            "viseme": self.viseme,
            "is_speaking": self.is_speaking,
            "is_listening": self.is_listening,
            "is_thinking": self.is_thinking,
            "head_rotation_deg": self.head_rotation_deg,
            "joint_angles": self.joint_angles,
            "active_layers": self.active_layers
        }
