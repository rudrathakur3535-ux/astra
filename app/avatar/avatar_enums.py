"""
Avatar Enums for Project Astra OS (v2.1 Enterprise Spec).
Defines character expression, outfit, gesture, eye focus, and gesture priority states
matching the official Astra character design reference sheets.
"""

from enum import Enum


class AstraEmotion(str, Enum):
    """
    25 facial expressions from the Official Astra Expression Sheet.
    """
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SMILE = "smile"
    EXCITED = "excited"
    LAUGHING = "laughing"
    BLUSH = "blush"
    THINKING = "thinking"
    CURIOUS = "curious"
    SERIOUS = "serious"
    FOCUSED = "focused"
    CONFIDENT = "confident"
    DETERMINED = "determined"
    SURPRISED = "surprised"
    SHOCKED = "shocked"
    WORRIED = "worried"
    SAD = "sad"
    ANGRY = "angry"
    DISAPPOINTED = "disappointed"
    TIRED = "tired"
    SLEEPY = "sleepy"
    RELAXED = "relaxed"
    PROUD = "proud"
    PLAYFUL = "playful"
    GREETING = "greeting"
    CONFUSED = "confused"
    SHY = "shy"

    @classmethod
    def from_string(cls, value: str) -> "AstraEmotion":
        """Parse a string into an AstraEmotion, falling back to NEUTRAL."""
        if not value:
            return cls.NEUTRAL
        clean = value.strip().lower()
        try:
            return cls(clean)
        except ValueError:
            return cls.NEUTRAL


class AstraOutfit(str, Enum):
    """
    6 outfit modes from the Official Astra Outfit Guide.
    """
    FOCUS = "focus"             # Coding, debugging, deep technical work
    RELAX = "relax"             # Casual chat, idle, small talk
    CREATIVE = "creative"       # Brainstorming, writing, design discussion
    TRAVEL = "travel"           # Directions, location, travel planning
    NIGHT = "night"             # Late-night sessions (time-of-day signal)
    PRESENTATION = "presentation"  # Demos, reports, formal summaries

    @classmethod
    def from_string(cls, value: str) -> "AstraOutfit":
        """Parse a string into an AstraOutfit, falling back to RELAX."""
        if not value:
            return cls.RELAX
        clean = value.strip().lower()
        try:
            return cls(clean)
        except ValueError:
            return cls.RELAX


class AstraGesture(str, Enum):
    """
    13 hand gestures from the Official Astra Hand Pose Sheet.
    """
    WAVE = "wave"
    POINT = "point"
    EXPLAIN = "explain"
    PRESENT = "present"
    WELCOME = "welcome"
    OK_SIGN = "ok_sign"
    THUMBS_UP = "thumbs_up"
    VICTORY = "victory"
    TYPING = "typing"
    THINKING = "thinking"
    STOP = "stop"
    NONE = "none"

    @classmethod
    def from_string(cls, value: str) -> "AstraGesture":
        """Parse a string into an AstraGesture, falling back to NONE."""
        if not value:
            return cls.NONE
        clean = value.strip().lower()
        try:
            return cls(clean)
        except ValueError:
            return cls.NONE


class AstraEyeFocus(str, Enum):
    """
    8 eye tracking gaze targets (v2.1 spec).
    """
    USER = "user"
    CAMERA = "camera"
    SCREEN = "screen"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    THINKING = "thinking"

    @classmethod
    def from_string(cls, value: str) -> "AstraEyeFocus":
        """Parse a string into an AstraEyeFocus, falling back to USER."""
        if not value:
            return cls.USER
        clean = value.strip().lower()
        try:
            return cls(clean)
        except ValueError:
            return cls.USER


class AstraGesturePriority(str, Enum):
    """
    Gesture priority levels (v2.1 spec).
    Critical gestures cannot be interrupted.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, value: str) -> "AstraGesturePriority":
        """Parse a string into an AstraGesturePriority, falling back to NORMAL."""
        if not value:
            return cls.NORMAL
        clean = value.strip().lower()
        try:
            return cls(clean)
        except ValueError:
            return cls.NORMAL
