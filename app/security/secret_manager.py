"""
Central Secret Manager for Project Astra OS.
Isolates API keys, environment credentials, and tokens from plain text exposure.
"""

from typing import Dict, Optional, Any
import os
from app.security.credential_store import CredentialStore
from app.ports.security_port import SecurityPort


class SecretManager:
    """
    Central Secret Manager exposing credentials safely to authorized components.
    """

    KNOWN_SECRETS = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "CHROMA_SERVER_KEY",
        "ASTRA_SECRET_KEY"
    ]

    def __init__(self, credential_store: Optional[CredentialStore] = None):
        self.credential_store = credential_store or CredentialStore()
        self._init_env_secrets()

    def _init_env_secrets(self) -> None:
        """Imports environment secrets into credential store if present."""
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ[k.strip()] = v.strip()
            except Exception:
                pass

        for secret_name in self.KNOWN_SECRETS:
            env_val = os.getenv(secret_name)
            if env_val:
                self.credential_store.set_credential(secret_name, env_val)

    def get_secret(self, secret_key: str) -> Optional[str]:
        """
        Retrieves a secret value. Checks CredentialStore first, then os.environ fallback.
        """
        val = self.credential_store.get_credential(secret_key)
        if val:
            return val
        return os.getenv(secret_key)

    def set_secret(self, secret_key: str, secret_value: str) -> None:
        """
        Stores a secret value securely.
        """
        self.credential_store.set_credential(secret_key, secret_value)

    def mask_secret(self, value: str) -> str:
        """
        Masks a secret string for logging or UI display (e.g. 'sk-12345678' -> 'sk-***5678').
        """
        if not value or len(value) <= 6:
            return "******"
        return f"{value[:3]}***{value[-4:]}"

    def get_masked_secret(self, secret_key: str) -> Optional[str]:
        """Retrieves masked secret value for safe UI display."""
        val = self.get_secret(secret_key)
        if val:
            return self.mask_secret(val)
        return None
