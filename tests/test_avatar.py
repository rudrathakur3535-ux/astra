"""
Unit Test Suite for Astra Interactive Avatar System (v2.1 Specification).
Verifies enums, state manager, LLM response parser v2.1, animation safety rules,
voice emotion mapping, and Avatar API endpoints.
"""

import pytest
import json
from fastapi.testclient import TestClient

from app.avatar import (
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
    AvatarState,
    AvatarStateManager,
    avatar_state_manager,
    parse_llm_response,
)
from app.brain.prompts import get_system_prompt
from app.main import app

client = TestClient(app)


def test_avatar_enums_v21_parsing():
    """Verifies enum string parsing and fallbacks for v2.1 enums."""
    assert AstraEmotion.from_string("happy") == AstraEmotion.HAPPY
    assert AstraEmotion.from_string("blush") == AstraEmotion.BLUSH
    assert AstraEmotion.from_string("non_existent") == AstraEmotion.NEUTRAL

    assert AstraOutfit.from_string("focus") == AstraOutfit.FOCUS
    assert AstraOutfit.from_string("invalid") == AstraOutfit.RELAX

    assert AstraGesture.from_string("stop") == AstraGesture.STOP
    assert AstraGesture.from_string("invalid") == AstraGesture.NONE

    assert AstraEyeFocus.from_string("camera") == AstraEyeFocus.CAMERA
    assert AstraEyeFocus.from_string("invalid") == AstraEyeFocus.USER

    assert AstraGesturePriority.from_string("critical") == AstraGesturePriority.CRITICAL
    assert AstraGesturePriority.from_string("invalid") == AstraGesturePriority.NORMAL


def test_v21_avatar_state_defaults():
    """Verifies AvatarState v2.1 field defaults and dictionary serialization."""
    state = AvatarState(
        emotion=AstraEmotion.EXCITED,
        emotion_strength=0.85,
        outfit_mode=AstraOutfit.CREATIVE,
        gesture=AstraGesture.VICTORY,
        gesture_priority=AstraGesturePriority.HIGH,
        gesture_duration=2.0,
        eye_focus=AstraEyeFocus.USER,
        reply_text="V2.1 state test"
    )
    data = state.to_dict()
    assert data["emotion"] == "excited"
    assert data["emotion_strength"] == 0.85
    assert data["outfit_mode"] == "creative"
    assert data["gesture"] == "victory"
    assert data["gesture_priority"] == "high"
    assert data["gesture_duration"] == 2.0
    assert data["eye_focus"] == "user"
    assert "speech_style" in data
    assert data["speech_style"]["speed"] == 1.0  # Dataclass default speed


def test_response_parser_v21_full_json():
    """Verifies v2.1 JSON output contract parsing."""
    raw_json = json.dumps({
        "reply": "System architecture review complete.",
        "emotion": "focused",
        "emotion_strength": 0.90,
        "speech_style": {
            "speed": 1.0,
            "pitch": 0.95,
            "energy": 0.80,
            "pause_level": 0.25
        },
        "eye_focus": "screen",
        "outfit_mode": "focus",
        "gesture": "explain",
        "gesture_priority": "high",
        "gesture_duration": 2.5,
        "tool_status": {
            "requires_tool": True,
            "tool": "code_analyzer"
        },
        "reasoning_hint": "User requested architecture review."
    })

    reply, state = parse_llm_response(raw_json)

    assert reply == "System architecture review complete."
    assert state.emotion == AstraEmotion.FOCUSED
    assert state.emotion_strength == 0.90
    assert state.outfit_mode == AstraOutfit.FOCUS
    assert state.gesture == AstraGesture.EXPLAIN
    assert state.gesture_priority == AstraGesturePriority.HIGH
    assert state.gesture_duration == 2.5
    assert state.eye_focus == AstraEyeFocus.SCREEN
    assert state.speech_style["speed"] == 1.0
    assert state.speech_style["energy"] == 0.80
    assert state.tool_status["requires_tool"] is True
    assert state.reasoning_hint == "User requested architecture review."


def test_animation_safety_rules():
    """Verifies animation safety rules (Rule #12): sad + victory -> NONE."""
    raw_json = json.dumps({
        "reply": "Unfortunately the build failed.",
        "emotion": "sad",
        "gesture": "victory"  # Incompatible with sad!
    })

    reply, state = parse_llm_response(raw_json)
    assert state.emotion == AstraEmotion.SAD
    assert state.gesture == AstraGesture.NONE  # Safety rule filtered out victory!


def test_metadata_validation_fallbacks():
    """Verifies metadata validation fallbacks (Rule #15)."""
    raw_json = json.dumps({
        "reply": "Testing invalid metadata fallbacks.",
        "emotion": "invalid_emotion_xyz",
        "emotion_strength": "invalid_number",
        "outfit_mode": "unknown_outfit",
        "gesture_priority": "super_high"
    })

    reply, state = parse_llm_response(raw_json)
    assert state.emotion == AstraEmotion.NEUTRAL
    assert state.emotion_strength == 0.50
    assert state.outfit_mode == AstraOutfit.RELAX
    assert state.gesture_priority == AstraGesturePriority.NORMAL


def test_system_prompt_v21_formatting():
    """Verifies system prompt v2.1 template generation and formatting."""
    prompt = get_system_prompt("Rudra")
    assert "Astra — Rudra's personal AI Operating System Companion" in prompt
    assert "emotion_strength" in prompt
    assert "speech_style" in prompt
    assert "eye_focus" in prompt
    assert "gesture_priority" in prompt
    assert "gesture_duration" in prompt
    assert "AVATAR BEHAVIOR & OUTFIT STABILITY RULES" in prompt
    assert "RENDERER INDEPENDENCE & FUTURE SCALABILITY" in prompt


def test_avatar_api_v21_endpoints():
    """Verifies REST API endpoints with v2.1 fields."""
    res = client.get("/avatar/state")
    assert res.status_code == 200
    data = res.json()
    assert "emotion_strength" in data
    assert "speech_style" in data
    assert "eye_focus" in data

    res = client.post("/avatar/state/manual", json={
        "emotion": "blush",
        "emotion_strength": 0.95,
        "outfit_mode": "creative",
        "gesture": "wave",
        "eye_focus": "camera",
        "reply_text": "v2.1 manual test"
    })
    assert res.status_code == 200
    res_data = res.json()["state"]
    assert res_data["emotion"] == "blush"
    assert res_data["emotion_strength"] == 0.95
    assert res_data["eye_focus"] == "camera"
