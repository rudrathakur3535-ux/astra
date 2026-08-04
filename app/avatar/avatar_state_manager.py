import time
from typing import Dict, Any, List, Optional
from app.models.avatar_state import AvatarState, ExpressionEnum, GestureEnum
from app.avatar.avatar_enums import VisemeEnum, AstraOutfit, AstraEyeFocus, AstraGesturePriority

class AvatarStateManager:
    def __init__(self):
        self.state = AvatarState()
        self._phoneme_queue: List[Dict[str, Any]] = []

    def set_expression(self, expression: ExpressionEnum) -> AvatarState:
        self.state.expression = expression
        return self.state

    def set_gesture(self, gesture: GestureEnum) -> AvatarState:
        self.state.gesture = gesture
        return self.state

    def queue_visemes(self, visemes: List[Dict[str, Any]]) -> None:
        self._phoneme_queue.extend(visemes)
        self.state.is_speaking = True

    def process_next_viseme(self) -> Optional[str]:
        if self._phoneme_queue:
            item = self._phoneme_queue.pop(0)
            self.state.viseme = item.get("viseme", VisemeEnum.CLOSED.value)
            if not self._phoneme_queue:
                self.state.is_speaking = False
            return self.state.viseme
        self.state.viseme = VisemeEnum.CLOSED.value
        self.state.is_speaking = False
        return self.state.viseme

    def update_state(self, new_state: AvatarState) -> AvatarState:
        self.state = new_state
        return self.state

    def update_from_response(
        self,
        reply_text: str = "",
        emotion: Any = ExpressionEnum.NEUTRAL,
        emotion_strength: float = 0.50,
        outfit_mode: Any = "relax",
        gesture: Any = GestureEnum.NONE,
        gesture_priority: Any = "normal",
        gesture_duration: float = 1.5,
        eye_focus: Any = "user",
        speech_style: Optional[Dict[str, float]] = None,
        tool_status: Optional[Dict[str, Any]] = None,
        reasoning_hint: str = ""
    ) -> AvatarState:
        self.state.reply_text = reply_text
        self.state.expression = emotion
        self.state.emotion_strength = emotion_strength
        self.state.outfit_mode = outfit_mode
        self.state.gesture = gesture
        self.state.gesture_priority = gesture_priority
        self.state.gesture_duration = gesture_duration
        self.state.eye_focus = eye_focus
        if speech_style:
            self.state.speech_style = speech_style
        if tool_status:
            self.state.tool_status = tool_status
        if reasoning_hint:
            self.state.reasoning_hint = reasoning_hint
        return self.state

    def get_state(self) -> AvatarState:
        return self.state

    def get_current_state(self) -> AvatarState:
        return self.state

    def get_state_dict(self) -> Dict[str, Any]:
        return self.state.to_dict()

    def to_websocket_payload(self) -> Dict[str, Any]:
        return {
            "type": "avatar_state_update",
            "timestamp": time.time(),
            "data": self.get_state_dict()
        }

avatar_state_manager = AvatarStateManager()
