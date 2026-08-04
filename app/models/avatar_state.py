from enum import Enum
from typing import Dict, Any, List
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
    expression: ExpressionEnum = ExpressionEnum.NEUTRAL
    gesture: GestureEnum = GestureEnum.NONE
    viseme: str = "mouth_closed"
    is_speaking: bool = False
    is_listening: bool = False
    is_thinking: bool = False
    eye_blink: bool = False
    head_rotation_deg: float = 0.0
    joint_angles: Dict[str, float] = Field(default_factory=dict)
    active_layers: List[str] = Field(default_factory=list)
