import re
import json
from typing import Tuple, List, Dict, Any, Union
from app.avatar.avatar_enums import (
    ExpressionEnum, GestureEnum, VisemeEnum,
    AstraEmotion, AstraGesture, AstraOutfit, AstraEyeFocus, AstraGesturePriority
)
from app.models.avatar_state import AvatarState

class ResponseParser:
    @staticmethod
    def parse_llm_response(raw_text: str) -> Union[Tuple[str, ExpressionEnum, GestureEnum, List[Dict[str, Any]]], Tuple[str, AvatarState]]:
        # Check if raw_text is a JSON string contract
        raw_text_trimmed = raw_text.strip()
        if raw_text_trimmed.startswith('{') and raw_text_trimmed.endswith('}'):
            try:
                data = json.loads(raw_text_trimmed)
                reply = data.get("reply", raw_text)
                
                emotion_str = str(data.get("emotion", "neutral"))
                emotion = AstraEmotion.from_string(emotion_str)

                try:
                    emotion_strength = float(data.get("emotion_strength", 0.50))
                except (ValueError, TypeError):
                    emotion_strength = 0.50

                outfit_str = str(data.get("outfit_mode", "relax"))
                outfit = AstraOutfit.from_string(outfit_str)

                gesture_str = str(data.get("gesture", "none"))
                gesture = AstraGesture.from_string(gesture_str)

                # Safety Rule: sad + victory -> NONE
                if emotion == AstraEmotion.SAD and gesture == AstraGesture.VICTORY:
                    gesture = AstraGesture.NONE

                prio_str = str(data.get("gesture_priority", "normal"))
                priority = AstraGesturePriority.from_string(prio_str)

                try:
                    duration = float(data.get("gesture_duration", 1.5))
                except (ValueError, TypeError):
                    duration = 1.5

                eye_str = str(data.get("eye_focus", "user"))
                eye_focus = AstraEyeFocus.from_string(eye_str)

                speech_style = data.get("speech_style", {"speed": 1.0, "pitch": 1.0, "energy": 0.5, "pause_level": 0.0})
                tool_status = data.get("tool_status", {"requires_tool": False, "tool": None})
                reasoning_hint = data.get("reasoning_hint", "")

                state = AvatarState(
                    expression=emotion,
                    gesture=gesture,
                    emotion_strength=emotion_strength,
                    outfit_mode=outfit,
                    gesture_priority=priority,
                    gesture_duration=duration,
                    eye_focus=eye_focus,
                    reply_text=reply,
                    speech_style=speech_style,
                    tool_status=tool_status,
                    reasoning_hint=reasoning_hint
                )
                return reply, state
            except Exception:
                pass

        # Text parsing for bracketed tags like [HAPPY], [GESTURE:WAVE]
        expression = ExpressionEnum.NEUTRAL
        gesture = GestureEnum.NONE

        expr_match = re.search(
            r"\[(HAPPY|SMILE|EXCITED|THINKING|CONFUSED|SURPRISED|ANGRY|SAD|WORRIED|BLUSH|FOCUSED)\]",
            raw_text,
            re.IGNORECASE
        )
        if expr_match:
            try:
                expression = ExpressionEnum(expr_match.group(1).lower())
            except ValueError:
                pass

        gesture_match = re.search(
            r"\[GESTURE:(WAVE|EXPLAIN|POINT|THUMBS_UP|THINKING|PRESENT|STOP|VICTORY)\]",
            raw_text,
            re.IGNORECASE
        )
        if gesture_match:
            try:
                gesture = GestureEnum(gesture_match.group(1).lower())
            except ValueError:
                pass

        # Remove control tags from spoken text output
        clean_text = re.sub(r"\[.*?\]", "", raw_text).strip()

        # Map clean speech characters to visemes for lip-sync animation
        visemes = []
        for char in clean_text.lower():
            if char in 'aeiou':
                visemes.append({"viseme": VisemeEnum.OPEN.value, "duration_ms": 120.0})
            elif char in (' ', '.', ','):
                visemes.append({"viseme": VisemeEnum.CLOSED.value, "duration_ms": 80.0})
            else:
                visemes.append({"viseme": VisemeEnum.SLIGHTLY_OPEN.value, "duration_ms": 90.0})

        return clean_text, expression, gesture, visemes

parse_llm_response = ResponseParser.parse_llm_response
