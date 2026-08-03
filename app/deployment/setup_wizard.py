"""
First-Time Onboarding & Setup Wizard Engine for Project Astra OS.
Enables quick setup (under 5 mins) without manual .env file editing.
"""

from typing import Dict, Any, Optional
from app.security.secret_manager import SecretManager
from app.services.settings_service import SettingsService


class SetupWizard:
    """
    Onboarding Setup Wizard for initializing AI providers, API keys, and voice settings.
    """

    def __init__(
        self,
        secret_manager: Optional[SecretManager] = None,
        settings_service: Optional[SettingsService] = None
    ):
        self.secret_manager = secret_manager or SecretManager()
        self.settings_service = settings_service or SettingsService()

    def run_setup(
        self,
        llm_provider: str = "openai",
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None,
        voice_engine: str = "elevenlabs",
        wake_word: str = "Hey Astra"
    ) -> Dict[str, Any]:
        """
        Executes first-time setup configuration and securely persists settings & secrets.
        """
        secrets_saved = []

        if openai_api_key:
            self.secret_manager.set_secret("OPENAI_API_KEY", openai_api_key)
            secrets_saved.append("OPENAI_API_KEY")

        if gemini_api_key:
            self.secret_manager.set_secret("GEMINI_API_KEY", gemini_api_key)
            secrets_saved.append("GEMINI_API_KEY")

        if elevenlabs_api_key:
            self.secret_manager.set_secret("ELEVENLABS_API_KEY", elevenlabs_api_key)
            secrets_saved.append("ELEVENLABS_API_KEY")

        updated_settings = self.settings_service.update_settings({
            "llm_provider": llm_provider,
            "voice_engine": voice_engine,
            "wake_word": wake_word,
            "setup_completed": True
        })

        return {
            "status": "success",
            "setup_completed": True,
            "llm_provider": llm_provider,
            "voice_engine": voice_engine,
            "secrets_configured": secrets_saved,
            "settings": updated_settings
        }

    def is_setup_completed(self) -> bool:
        """Checks if first-time onboarding setup has been completed."""
        return bool(self.settings_service.get_setting("setup_completed", False))
