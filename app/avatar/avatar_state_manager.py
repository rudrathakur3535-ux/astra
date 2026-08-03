"""
Avatar State Manager for Project Astra OS (v2.1 Enterprise Spec).
Singleton managing global character state, transitions, eye tracking, lip-sync,
and WebSocket subscriber notifications.
"""

import time
import asyncio
from typing import List, Callable, Optional, Dict, Any

from app.avatar.avatar_enums import (
    AstraEmotion,
    AstraOutfit,
    AstraGesture,
    AstraEyeFocus,
    AstraGesturePriority,
)
from app.avatar.avatar_state import AvatarState
from app.utils.logger import logger


class AvatarStateManager:
    """
    Central coordinator for Astra's character state.
    """

    def __init__(self):
        self._state = AvatarState()
        self._subscribers: List[asyncio.Queue] = []
        self._state_history: List[Dict[str, Any]] = []
        self._max_history = 50

    def get_current_state(self) -> AvatarState:
        """Returns current avatar state snapshot."""
        return self._state.copy()

    def get_state_dict(self) -> Dict[str, Any]:
        """Returns current state as a JSON-serializable dict."""
        return self._state.to_dict()

    def update_from_response(
        self,
        reply_text: str,
        emotion: AstraEmotion = AstraEmotion.NEUTRAL,
        outfit_mode: AstraOutfit = AstraOutfit.RELAX,
        gesture: AstraGesture = AstraGesture.NONE,
        emotion_strength: float = 0.50,
        speech_style: Optional[Dict[str, float]] = None,
        eye_focus: AstraEyeFocus = AstraEyeFocus.USER,
        gesture_priority: AstraGesturePriority = AstraGesturePriority.NORMAL,
        gesture_duration: float = 1.5,
        tool_status: Optional[Dict[str, Any]] = None,
        reasoning_hint: str = "",
    ) -> AvatarState:
        """
        Apply full state update from parsed LLM v2.1 response.
        Supports full backward compatibility for v2.0 callers.
        """
        self._state.emotion = emotion
        self._state.emotion_strength = max(0.0, min(1.0, emotion_strength))

        # Outfit Stability Rule: only update outfit if provided and valid
        if outfit_mode:
            self._state.outfit_mode = outfit_mode

        self._state.gesture = gesture
        self._state.gesture_priority = gesture_priority
        self._state.gesture_duration = max(0.1, gesture_duration)
        self._state.eye_focus = eye_focus

        if speech_style:
            self._state.speech_style = speech_style
        if tool_status:
            self._state.tool_status = tool_status

        self._state.reasoning_hint = reasoning_hint
        self._state.reply_text = reply_text
        self._state.is_thinking = False
        self._state.last_updated = time.time()

        logger.info(
            f"Avatar state updated: emotion={emotion.value} ({emotion_strength:.2f}), "
            f"outfit={self._state.outfit_mode.value}, gesture={gesture.value} ({gesture_priority.value})"
        )

        self._record_history()
        self._notify_subscribers()
        return self._state.copy()

    def update_from_state_object(self, new_state: AvatarState) -> AvatarState:
        """Apply state from an AvatarState object directly."""
        return self.update_from_response(
            reply_text=new_state.reply_text,
            emotion=new_state.emotion,
            outfit_mode=new_state.outfit_mode,
            gesture=new_state.gesture,
            emotion_strength=new_state.emotion_strength,
            speech_style=new_state.speech_style,
            eye_focus=new_state.eye_focus,
            gesture_priority=new_state.gesture_priority,
            gesture_duration=new_state.gesture_duration,
            tool_status=new_state.tool_status,
            reasoning_hint=new_state.reasoning_hint,
        )

    def set_speaking(self, active: bool) -> None:
        """Toggle speaking flag (triggers lip-sync)."""
        if self._state.is_speaking != active:
            self._state.is_speaking = active
            self._state.last_updated = time.time()
            if not active:
                self._state.mouth_openness = 0.0
            logger.debug(f"Avatar speaking: {active}")
            self._notify_subscribers()

    def set_listening(self, active: bool) -> None:
        """Toggle listening flag (triggers listening pose)."""
        if self._state.is_listening != active:
            self._state.is_listening = active
            self._state.last_updated = time.time()
            if active:
                self._state.emotion = AstraEmotion.CURIOUS
                self._state.eye_focus = AstraEyeFocus.USER
            logger.debug(f"Avatar listening: {active}")
            self._notify_subscribers()

    def set_thinking(self, active: bool) -> None:
        """Toggle thinking flag (pauses eye tracking per behavior rules)."""
        if self._state.is_thinking != active:
            self._state.is_thinking = active
            self._state.last_updated = time.time()
            if active:
                self._state.emotion = AstraEmotion.THINKING
                self._state.gesture = AstraGesture.THINKING
                self._state.eye_focus = AstraEyeFocus.THINKING
            else:
                self._state.eye_focus = AstraEyeFocus.USER
            logger.debug(f"Avatar thinking: {active}")
            self._notify_subscribers()

    def update_eye_target(self, x: float, y: float) -> None:
        """Update eye tracking target from frontend cursor position (if not thinking)."""
        if self._state.is_thinking:
            return  # Rule: Eye tracking pauses during thinking

        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))

        dx = abs(self._state.eye_target_x - x)
        dy = abs(self._state.eye_target_y - y)
        if dx > 0.01 or dy > 0.01:
            self._state.eye_target_x = x
            self._state.eye_target_y = y
            self._notify_subscribers()

    def update_mouth_openness(self, amplitude: float) -> None:
        """Update mouth openness amplitude for voice lip-sync."""
        self._state.mouth_openness = max(0.0, min(1.0, amplitude))
        self._notify_subscribers()

    def reset_gesture(self) -> None:
        """Reset gesture to NONE (called after gesture display timeout unless CRITICAL)."""
        if (
            self._state.gesture != AstraGesture.NONE
            and self._state.gesture_priority != AstraGesturePriority.CRITICAL
        ):
            self._state.gesture = AstraGesture.NONE
            self._state.gesture_priority = AstraGesturePriority.NORMAL
            self._state.last_updated = time.time()
            self._notify_subscribers()

    def subscribe(self) -> asyncio.Queue:
        """Register WebSocket subscriber queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Remove WebSocket subscriber queue."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def _notify_subscribers(self) -> None:
        """Push state dict to all subscribers."""
        state_dict = self._state.to_dict()
        dead_queues = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(state_dict)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                    queue.put_nowait(state_dict)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    dead_queues.append(queue)

        for q in dead_queues:
            self._subscribers.remove(q)

    def _record_history(self) -> None:
        """Record state snapshot for timeline / logs."""
        entry = self._state.to_dict()
        self._state_history.append(entry)
        if len(self._state_history) > self._max_history:
            self._state_history = self._state_history[-self._max_history:]

    def get_history(self) -> List[Dict[str, Any]]:
        """Returns recent state transitions history."""
        return list(self._state_history)


avatar_state_manager = AvatarStateManager()
