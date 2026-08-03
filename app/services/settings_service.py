"""
Application Settings Service for Project Astra OS.
Provides dynamic configuration management, AI provider selection, voice settings, and plugin permissions.
"""

from typing import Dict, Any, Optional
import json
import os


class SettingsService:
    """
    Manages dynamic application settings and configuration persistence.
    """

    DEFAULT_SETTINGS: Dict[str, Any] = {
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "voice_engine": "elevenlabs",
        "voice_name": "Rachel",
        "wake_word": "Hey Astra",
        "theme": "dark",
        "auto_start_browser": True,
        "max_context_tokens": 4096,
        "plugin_permissions": {
            "web_search": True,
            "code_analyzer": True,
            "terminal_control": False
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "app/config/settings.json"
        self._settings: Dict[str, Any] = dict(self.DEFAULT_SETTINGS)
        self._load_settings()

    def _load_settings(self) -> None:
        """Loads settings from JSON file if available."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._settings.update(data)
            except Exception:
                pass

    def save_settings(self) -> bool:
        """Saves current settings to JSON configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=2)
            return True
        except Exception:
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Retrieves a setting value."""
        return self._settings.get(key, default)

    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates setting key-values and persists to disk."""
        self._settings.update(updates)
        self.save_settings()
        return dict(self._settings)

    def get_all_settings(self) -> Dict[str, Any]:
        """Returns all configuration settings."""
        return dict(self._settings)
