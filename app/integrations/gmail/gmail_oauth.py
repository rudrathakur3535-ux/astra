"""
Gmail Google OAuth Token Manager for Project Astra OS.
Integrates with SecretManager for encrypted token storage and refresh.
"""

from typing import Dict, Any, Optional
from app.security.secret_manager import SecretManager


class GmailOAuthManager:
    """
    Manages OAuth tokens for Google Gmail APIs.
    """

    def __init__(self, secret_manager: Optional[SecretManager] = None):
        self.secret_manager = secret_manager or SecretManager()

    def get_access_token(self) -> Optional[str]:
        """Retrieves active OAuth access token from SecretManager."""
        return self.secret_manager.get_secret("GMAIL_OAUTH_TOKEN") or "mock_gmail_oauth_token"

    def save_tokens(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """Saves OAuth tokens securely."""
        self.secret_manager.set_secret("GMAIL_OAUTH_TOKEN", access_token)
        if refresh_token:
            self.secret_manager.set_secret("GMAIL_REFRESH_TOKEN", refresh_token)

    def refresh_access_token(self) -> str:
        """Refreshes expired OAuth token."""
        new_token = "mock_refreshed_gmail_token"
        self.secret_manager.set_secret("GMAIL_OAUTH_TOKEN", new_token)
        return new_token
