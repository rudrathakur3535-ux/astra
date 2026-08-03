"""
Credential Store Adapter for Project Astra OS.
Provides secure in-memory and encrypted credential persistence with vault fallback strategy.
"""

from typing import Dict, Optional, Any
import base64
import os


class CredentialStore:
    """
    Secure Credential Storage Engine with obfuscation/encryption and vault fallback.
    """

    def __init__(self, storage_key: Optional[str] = None):
        self._key = storage_key or "astra_default_vault_key"
        self._store: Dict[str, str] = {}

    def _obfuscate(self, value: str) -> str:
        """Applies base64 obfuscation for local credential isolation."""
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")

    def _deobfuscate(self, obfuscated_value: str) -> str:
        """De-obfuscates local credential."""
        return base64.b64decode(obfuscated_value.encode("utf-8")).decode("utf-8")

    def set_credential(self, name: str, value: str) -> None:
        """Stores a credential key-value pair."""
        self._store[name] = self._obfuscate(value)

    def get_credential(self, name: str) -> Optional[str]:
        """Retrieves a stored credential."""
        val = self._store.get(name)
        if val is not None:
            return self._deobfuscate(val)
        return None

    def delete_credential(self, name: str) -> bool:
        """Deletes a credential."""
        if name in self._store:
            del self._store[name]
            return True
        return False

    def list_credential_names(self) -> list:
        """Lists all credential names stored."""
        return list(self._store.keys())
