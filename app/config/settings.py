import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

class Settings:
    """Project Astra application configuration settings."""
    APP_NAME: str = os.getenv("APP_NAME", "Project Astra")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

settings = Settings()
