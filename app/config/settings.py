import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseModel):
    """Central configuration class for Project Astra using Pydantic validation."""

    APP_NAME: str = Field(default="Project Astra", description="Application name")
    APP_ENV: str = Field(default="development", description="Environment mode")
    DEBUG: bool = Field(default=True, description="Debug flag")
    USER_NAME: str = Field(default="Rudra", description="Primary user name")

    # LLM Settings
    OPENAI_API_KEY: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key"
    )
    GEMINI_API_KEY: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", ""),
        description="Gemini API key"
    )
    MODEL: str = Field(
        default_factory=lambda: os.getenv("MODEL", "gemini-1.5-flash"),
        description="LLM Model identifier"
    )
    DEFAULT_TEMPERATURE: float = Field(default=0.7, description="Default generation temperature")
    MAX_TOKENS: int = Field(default=2048, description="Max output tokens")

    # Voice & Audio Settings
    ELEVENLABS_API_KEY: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""),
        description="ElevenLabs API key for TTS"
    )
    ELEVENLABS_VOICE_ID: str = Field(
        default_factory=lambda: os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        description="ElevenLabs Female Voice ID (Default: Rachel)"
    )
    WAKE_WORD: str = Field(
        default_factory=lambda: os.getenv("WAKE_WORD", "hey astra"),
        description="Wake word trigger string"
    )
    SAMPLE_RATE: int = Field(default=16000, description="Audio sampling rate in Hz")
    AUDIO_CHANNELS: int = Field(default=1, description="Audio channels (mono)")
    VOICE_ENABLED: bool = Field(
        default_factory=lambda: os.getenv("VOICE_ENABLED", "True").lower() in ("true", "1", "t"),
        description="Voice mode enabled flag"
    )

    # Logging Settings
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level"
    )
    LOG_FILE: str = Field(
        default_factory=lambda: os.getenv("LOG_FILE", "app/logs/astra.log"),
        description="Log file path"
    )

    @property
    def is_api_key_valid(self) -> bool:
        """Returns True if a non-placeholder OpenAI or Gemini API key is set."""
        from app.security.secret_manager import SecretManager
        sm = SecretManager()
        gemini_key = sm.get_secret("GEMINI_API_KEY") or self.GEMINI_API_KEY.strip()
        openai_key = sm.get_secret("OPENAI_API_KEY") or self.OPENAI_API_KEY.strip()

        has_gemini = bool(gemini_key) and gemini_key != "your_gemini_api_key_here"
        has_openai = bool(openai_key) and openai_key != "your_openai_api_key_here"
        return has_gemini or has_openai

    @property
    def is_elevenlabs_key_valid(self) -> bool:
        """Returns True if a non-placeholder ElevenLabs API key is set."""
        from app.security.secret_manager import SecretManager
        key = SecretManager().get_secret("ELEVENLABS_API_KEY") or self.ELEVENLABS_API_KEY.strip()
        return bool(key) and key != "your_elevenlabs_api_key_here"

settings = Settings()
