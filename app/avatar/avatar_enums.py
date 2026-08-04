from enum import Enum

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
    BLUSH = "blush"
    FOCUSED = "focused"

    @classmethod
    def from_string(cls, val: str) -> "ExpressionEnum":
        try:
            return cls(val.lower())
        except Exception:
            return cls.NEUTRAL

class GestureEnum(str, Enum):
    NONE = "none"
    WAVE = "wave"
    EXPLAIN = "explain"
    POINT = "point"
    THUMBS_UP = "thumbs_up"
    THINKING = "thinking"
    PRESENT = "present"
    STOP = "stop"
    VICTORY = "victory"

    @classmethod
    def from_string(cls, val: str) -> "GestureEnum":
        try:
            return cls(val.lower())
        except Exception:
            return cls.NONE

class VisemeEnum(str, Enum):
    CLOSED = "mouth_closed"
    SLIGHTLY_OPEN = "mouth_slightly_open"
    OPEN = "mouth_open"
    WIDE = "mouth_wide"

class AstraOutfit(str, Enum):
    RELAX = "relax"
    FOCUS = "focus"
    CREATIVE = "creative"

    @classmethod
    def from_string(cls, val: str) -> "AstraOutfit":
        try:
            return cls(val.lower())
        except Exception:
            return cls.RELAX

class AstraEyeFocus(str, Enum):
    USER = "user"
    CAMERA = "camera"
    SCREEN = "screen"

    @classmethod
    def from_string(cls, val: str) -> "AstraEyeFocus":
        try:
            return cls(val.lower())
        except Exception:
            return cls.USER

class AstraGesturePriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, val: str) -> "AstraGesturePriority":
        try:
            return cls(val.lower())
        except Exception:
            return cls.NORMAL

# Aliases for backwards compatibility & v2.1 spec
AstraEmotion = ExpressionEnum
AstraGesture = GestureEnum
AstraViseme = VisemeEnum
