"""
LLM Response Parser for Project Astra OS (v2.1 Enterprise Specification).
Extracts structured avatar metadata (emotion, emotion_strength, speech_style, eye_focus,
outfit_mode, gesture, gesture_priority, gesture_duration, tool_status, reasoning_hint)
from the LLM's JSON output with full validation fallbacks and animation safety rules.
"""

import json
import re
from typing import Tuple, Optional, Dict, Any

from app.avatar.avatar_enums import (
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
)
from app.avatar.avatar_state import AvatarState
from app.utils.logger import logger


def parse_llm_response(raw_response: str) -> Tuple[str, AvatarState]:
    """
    Parse an LLM response into user-facing reply text and v2.1 AvatarState.

    Args:
        raw_response: Raw completion string from LLM.

    Returns:
        Tuple of (reply_text, AvatarState).
    """
    if not raw_response or not raw_response.strip():
        return "", AvatarState()

    raw = raw_response.strip()

    # Attempt 1: Direct JSON parse
    parsed = _try_parse_json(raw)
    if parsed:
        return _extract_from_dict(parsed)

    # Attempt 2: Extract JSON block from markdown code fences
    json_block = _extract_json_block(raw)
    if json_block:
        parsed = _try_parse_json(json_block)
        if parsed:
            return _extract_from_dict(parsed)

    # Attempt 3: Find JSON object within raw text
    json_match = _find_json_in_text(raw)
    if json_match:
        parsed = _try_parse_json(json_match)
        if parsed:
            return _extract_from_dict(parsed)

    # Fallback: Plain text parsing with metadata inference
    logger.debug("LLM response is plain text — applying fallback validation rules")
    state = AvatarState(reply_text=raw)
    state.emotion = _infer_emotion_from_text(raw)
    return raw, state


def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Attempt to parse string as JSON dictionary."""
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _extract_json_block(text: str) -> Optional[str]:
    """Extract JSON string from markdown code fences."""
    pattern = r'```(?:json)?\s*\n?(.*?)\n?\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _find_json_in_text(text: str) -> Optional[str]:
    """Find first JSON object {...} in text."""
    depth = 0
    start = None
    for i, char in enumerate(text):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i + 1]
    return None


def _extract_from_dict(data: Dict[str, Any]) -> Tuple[str, AvatarState]:
    """
    Extract reply text and AvatarState from dict with v2.1 validation rules & fallbacks.
    """
    # 1. Reply Text
    reply = data.get("reply", "")
    if not reply and "response" in data:
        reply = data.get("response", "")
    if not reply and "text" in data:
        reply = data.get("text", "")
    if not isinstance(reply, str):
        reply = str(reply)

    # 2. Enums with Fallbacks (Metadata Validation Rule #15)
    emotion = AstraEmotion.from_string(data.get("emotion", "neutral"))
    outfit_mode = AstraOutfit.from_string(data.get("outfit_mode", "relax"))
    gesture = AstraGesture.from_string(data.get("gesture", "none"))
    eye_focus = AstraEyeFocus.from_string(data.get("eye_focus", "user"))
    gesture_priority = AstraGesturePriority.from_string(data.get("gesture_priority", "normal"))

    # 3. Emotion Strength (Range: 0.0 - 1.0, default: 0.50)
    try:
        emotion_strength = float(data.get("emotion_strength", 0.50))
        emotion_strength = max(0.0, min(1.0, emotion_strength))
    except (ValueError, TypeError):
        emotion_strength = 0.50

    # 4. Gesture Duration (seconds, default: 1.5)
    try:
        gesture_duration = float(data.get("gesture_duration", 1.5))
        gesture_duration = max(0.1, gesture_duration)
    except (ValueError, TypeError):
        gesture_duration = 1.5

    # 5. Speech Style object
    speech_style_raw = data.get("speech_style", {})
    if not isinstance(speech_style_raw, dict):
        speech_style_raw = {}
    speech_style = _compute_speech_style(emotion, speech_style_raw)

    # 6. Tool Status & Reasoning Hint
    tool_status_raw = data.get("tool_status", {})
    if not isinstance(tool_status_raw, dict):
        tool_status_raw = {"requires_tool": False, "tool": "none"}

    reasoning_hint = str(data.get("reasoning_hint", ""))

    # 7. Animation Safety Rules Enforcement (Rule #12)
    gesture = _enforce_animation_safety(emotion, gesture)

    state = AvatarState(
        emotion=emotion,
        emotion_strength=emotion_strength,
        outfit_mode=outfit_mode,
        gesture=gesture,
        gesture_priority=gesture_priority,
        gesture_duration=gesture_duration,
        eye_focus=eye_focus,
        speech_style=speech_style,
        tool_status=tool_status_raw,
        reasoning_hint=reasoning_hint,
        reply_text=reply,
    )

    logger.debug(
        f"Parsed v2.1 avatar state: emotion={emotion.value} ({emotion_strength:.2f}), "
        f"gesture={gesture.value}, eye={eye_focus.value}"
    )

    return reply, state


def _enforce_animation_safety(emotion: AstraEmotion, gesture: AstraGesture) -> AstraGesture:
    """
    Enforces Animation Safety Rules (Rule #12):
    Prevents impossible or contradictory emotion + gesture combinations.
    """
    # Sad / Worried / Disappointed cannot do Victory or Thumbs Up
    if emotion in (AstraEmotion.SAD, AstraEmotion.WORRIED, AstraEmotion.DISAPPOINTED, AstraEmotion.TIRED):
        if gesture in (AstraGesture.VICTORY, AstraGesture.THUMBS_UP, AstraGesture.OK_SIGN):
            return AstraGesture.NONE

    # Angry cannot do Victory or Welcome
    if emotion == AstraEmotion.ANGRY:
        if gesture in (AstraGesture.VICTORY, AstraGesture.WELCOME, AstraGesture.OK_SIGN):
            return AstraGesture.NONE

    return gesture


def _compute_speech_style(emotion: AstraEmotion, raw_style: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes voice emotion mapping defaults (Rule #13) if not provided by LLM.
    """
    defaults = {
        "speed": 1.0,
        "pitch": 0.95,
        "energy": 0.75,
        "pause_level": 0.30
    }

    if emotion in (AstraEmotion.HAPPY, AstraEmotion.EXCITED, AstraEmotion.LAUGHING):
        defaults = {"speed": 1.10, "pitch": 1.02, "energy": 0.85, "pause_level": 0.20}
    elif emotion in (AstraEmotion.SAD, AstraEmotion.TIRED, AstraEmotion.SLEEPY, AstraEmotion.DISAPPOINTED):
        defaults = {"speed": 0.85, "pitch": 0.90, "energy": 0.40, "pause_level": 0.50}
    elif emotion in (AstraEmotion.THINKING, AstraEmotion.FOCUSED, AstraEmotion.SERIOUS):
        defaults = {"speed": 0.95, "pitch": 0.95, "energy": 0.65, "pause_level": 0.40}

    # Override with valid LLM provided values
    for k in ("speed", "pitch", "energy", "pause_level"):
        if k in raw_style:
            try:
                val = float(raw_style[k])
                defaults[k] = max(0.1, min(2.0, val))
            except (ValueError, TypeError):
                pass

    return defaults


def _infer_emotion_from_text(text: str) -> AstraEmotion:
    """Fallback keyword-based emotion inference for plain text."""
    lower = text.lower()
    keywords = {
        AstraEmotion.HAPPY: ["great", "awesome", "wonderful", "excellent", "glad", "happy"],
        AstraEmotion.EXCITED: ["exciting", "amazing", "incredible", "wow", "fantastic"],
        AstraEmotion.THINKING: ["let me think", "considering", "analyzing", "hmm", "let me check"],
        AstraEmotion.CURIOUS: ["interesting", "curious", "tell me more", "wondering"],
        AstraEmotion.SERIOUS: ["important", "critical", "warning", "careful", "caution"],
        AstraEmotion.WORRIED: ["error", "failed", "problem", "issue", "broken", "sorry"],
        AstraEmotion.CONFIDENT: ["done", "completed", "successfully", "ready", "finished"],
        AstraEmotion.GREETING: ["hello", "hi ", "hey ", "welcome", "good morning"],
        AstraEmotion.SAD: ["unfortunately", "cannot", "unable", "impossible"],
        AstraEmotion.SURPRISED: ["unexpected", "surprisingly", "didn't expect"],
        AstraEmotion.PLAYFUL: ["haha", "lol", "fun", "joke"],
        AstraEmotion.FOCUSED: ["code", "debug", "implement", "function", "class"],
    }

    for emotion, kws in keywords.items():
        for kw in kws:
            if kw in lower:
                return emotion

    return AstraEmotion.NEUTRAL
