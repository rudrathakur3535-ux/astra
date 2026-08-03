"""
Authentication Engine for Project Astra OS.
Provides credential validation, API key verification, and token authentication.
"""

from typing import Dict, Optional, Any
import hashlib
import hmac
from app.security.identity_manager import IdentityManager
from app.models.user_identity import UserIdentity


class AuthenticationEngine:
    """
    Authenticates user identities, API keys, and credentials.
    """

    def __init__(self, identity_manager: Optional[IdentityManager] = None):
        self.identity_manager = identity_manager or IdentityManager()
        self._user_credentials: Dict[str, str] = {}  # username -> hashed_password
        self._api_keys: Dict[str, str] = {}          # api_key_hash -> user_id
        self._init_default_credentials()

    def _hash_password(self, password: str) -> str:
        """Hashes password with SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _init_default_credentials(self) -> None:
        """Initializes default owner password for local OS access."""
        owner = self.identity_manager.get_user("astra_owner")
        if owner:
            self._user_credentials[owner.username] = self._hash_password("astra_owner_pass")

    def register_credentials(self, username: str, password: str) -> bool:
        """Registers password credentials for a user."""
        user = self.identity_manager.get_user(username)
        if not user or not user.is_active:
            return False
        self._user_credentials[username] = self._hash_password(password)
        return True

    def authenticate_password(self, username: str, password: str) -> Optional[UserIdentity]:
        """Authenticates user with username and password."""
        user = self.identity_manager.get_user(username)
        if not user or not user.is_active:
            return None

        stored_hash = self._user_credentials.get(username)
        if stored_hash and hmac.compare_digest(stored_hash, self._hash_password(password)):
            return user
        return None

    def register_api_key(self, user_id: str, raw_api_key: str) -> bool:
        """Registers an API key for a user."""
        user = self.identity_manager.get_user(user_id)
        if not user:
            return False
        key_hash = hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()
        self._api_keys[key_hash] = user.user_id
        return True

    def authenticate_api_key(self, raw_api_key: str) -> Optional[UserIdentity]:
        """Authenticates user via raw API key."""
        key_hash = hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()
        user_id = self._api_keys.get(key_hash)
        if user_id:
            return self.identity_manager.get_user(user_id)
        return None
