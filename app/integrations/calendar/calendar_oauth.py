"""
Google Calendar OAuth Manager for Project Astra OS.
"""

from typing import Optional
from app.security.secret_manager import SecretManager


class CalendarOAuthManager:
    """
    Manages OAuth tokens for Google Calendar APIs.
    """

    def __init__(self, secret_manager: Optional[SecretManager] = None):
        self.secret_manager = secret_manager or SecretManager()

    def get_access_token(self) -> Optional[str]:
        return self.secret_manager.get_secret("CALENDAR_OAUTH_TOKEN") or "mock_calendar_oauth_token"
