"""
Integration Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class IntegrationPort(ABC):
    """
    Abstract Hexagonal Port interface for external integration adapters.
    """

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticates with external integration API."""
        pass

    @abstractmethod
    def fetch_context(self) -> Dict[str, Any]:
        """Fetches current domain context payload."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Returns connection status."""
        pass
