"""
Integration & Unit Test Suite for Desktop Experience (Electron + React) & Desktop APIs.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.services.settings_service import SettingsService
from app.services.desktop_bridge import DesktopBridge
from app.api.app_api import router as app_router


class TestSettingsService:
    """Tests application settings management and persistence."""

    def test_default_settings_loading(self, tmp_path):
        config_file = str(tmp_path / "settings.json")
        service = SettingsService(config_path=config_file)
        assert service.get_setting("llm_provider") == "openai"
        assert service.get_setting("theme") == "dark"

    def test_settings_update_and_persistence(self, tmp_path):
        config_file = str(tmp_path / "settings.json")
        service = SettingsService(config_path=config_file)
        service.update_settings({"llm_provider": "gemini", "theme": "cyberpunk"})

        assert service.get_setting("llm_provider") == "gemini"
        assert service.get_setting("theme") == "cyberpunk"

        # Re-load from disk
        reloaded = SettingsService(config_path=config_file)
        assert reloaded.get_setting("llm_provider") == "gemini"


class TestDesktopBridge:
    """Tests DesktopBridge events and state toggling."""

    def test_voice_status_toggles(self):
        bridge = DesktopBridge()
        assert bridge.get_voice_status()["is_listening"] is False

        updated = bridge.set_voice_listening(True)
        assert updated["is_listening"] is True

        wakeword_updated = bridge.set_wakeword_active(False)
        assert wakeword_updated["wakeword_active"] is False

    def test_event_listener_dispatch(self):
        bridge = DesktopBridge()
        listener_mock = MagicMock()
        bridge.register_event_listener(listener_mock)

        bridge.set_voice_listening(True)
        listener_mock.assert_called_once_with("voice_status_changed", bridge.get_voice_status())


class TestDesktopAPIEndpoints:
    """Tests FastAPI Application API Router endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(app_router)
        self.client = TestClient(self.app)

    def test_chat_prompt_processing(self):
        res = self.client.post("/api/chat", json={"prompt": "Summarize workspace"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "Executed workflow" in data["response"]

    def test_empty_chat_prompt_rejected(self):
        res = self.client.post("/api/chat", json={"prompt": ""})
        assert res.status_code == 400

    def test_get_and_update_settings_api(self):
        get_res = self.client.get("/api/settings")
        assert get_res.status_code == 200
        assert "llm_provider" in get_res.json()

        update_res = self.client.post("/api/settings", json={"theme": "dark_glass"})
        assert update_res.status_code == 200
        assert update_res.json()["settings"]["theme"] == "dark_glass"

    def test_plugins_api(self):
        res = self.client.get("/api/plugins")
        assert res.status_code == 200
        plugins = res.json()["plugins"]
        assert len(plugins) >= 2

        toggle_res = self.client.post("/api/plugins/toggle", json={"plugin_id": "web_search"})
        assert toggle_res.status_code == 200

    def test_voice_status_api(self):
        res = self.client.get("/api/voice/status")
        assert res.status_code == 200
        assert "is_listening" in res.json()

        toggle_res = self.client.post("/api/voice/toggle-listening", json={"listening": True})
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_listening"] is True
