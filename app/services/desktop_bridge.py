"""
Desktop Bridge Service for Project Astra OS.
Unifies Desktop IPC events, Voice subsystem controls, Multi-Agent runtime events, and UI streams.
"""

from typing import Dict, Any, Optional, List, Callable
import time
from app.services.settings_service import SettingsService


class DesktopBridge:
    """
    Bridge integrating Desktop UI actions with Astra core subsystems.
    """

    def __init__(self, settings_service: Optional[SettingsService] = None):
        self.settings_service = settings_service or SettingsService()
        self._active_agents: List[Dict[str, Any]] = []
        self._voice_state = {
            "is_listening": False,
            "stt_engine": "Whisper",
            "tts_engine": "ElevenLabs",
            "wakeword_active": True,
            "health": "healthy"
        }
        self._listeners: List[Callable[[str, Dict[str, Any]], None]] = []

    def register_event_listener(self, listener: Callable[[str, Dict[str, Any]], None]) -> None:
        """Registers a listener for UI desktop bridge events."""
        self._listeners.append(listener)

    def dispatch_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Dispatches an event to registered listeners."""
        for listener in self._listeners:
            try:
                listener(event_type, data)
            except Exception:
                pass

    def get_voice_status(self) -> Dict[str, Any]:
        """Returns current voice subsystem status."""
        return dict(self._voice_state)

    def set_voice_listening(self, listening: bool) -> Dict[str, Any]:
        """Toggles voice listening state."""
        self._voice_state["is_listening"] = listening
        self.dispatch_event("voice_status_changed", self._voice_state)
        return dict(self._voice_state)

    def set_wakeword_active(self, active: bool) -> Dict[str, Any]:
        """Toggles wake word detection state."""
        self._voice_state["wakeword_active"] = active
        self.dispatch_event("wakeword_status_changed", self._voice_state)
        return dict(self._voice_state)

    def get_active_agents(self) -> List[Dict[str, Any]]:
        """Returns currently active agent execution topology."""
        return list(self._active_agents)

    def set_active_agents(self, agents: List[Dict[str, Any]]) -> None:
        """Updates active agent execution topology."""
        self._active_agents = list(agents)
        self.dispatch_event("agents_topology_changed", {"agents": self._active_agents})
