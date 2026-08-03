"""
Security Port Interface for Project Astra OS (Hexagonal Architecture).
Defines abstract interfaces for Security, Credential Storage, and Secret Management Adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.models.user_identity import UserIdentity
from app.models.audit_record import AuditRecord
from app.models.security_event import SecurityEvent


class SecurityPort(ABC):
    """
    Abstract Hexagonal Port interface for Security Services.
    """

    @abstractmethod
    def authenticate(self, username: str, credentials: Dict[str, Any]) -> Optional[UserIdentity]:
        """Authenticates user credentials."""
        pass

    @abstractmethod
    def authorize(self, user_id: str, action: str, resource: str) -> bool:
        """Evaluates whether an action is authorized."""
        pass

    @abstractmethod
    def get_secret(self, secret_key: str) -> Optional[str]:
        """Retrieves a secret key value."""
        pass

    @abstractmethod
    def store_secret(self, secret_key: str, secret_value: str) -> bool:
        """Stores a secret key value securely."""
        pass

    @abstractmethod
    def log_audit(self, record: AuditRecord) -> None:
        """Logs an immutable audit record."""
        pass

    @abstractmethod
    def log_security_event(self, event: SecurityEvent) -> None:
        """Logs a security alert event."""
        pass
