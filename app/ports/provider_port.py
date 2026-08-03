"""
Provider Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.models.provider_status import ProviderStatus


class ProviderPort(ABC):
    """
    Abstract Hexagonal Port interface for LLM Provider Adapters.
    """

    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generates LLM text response."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generates vector embedding for text."""
        pass

    @abstractmethod
    def get_status(self) -> ProviderStatus:
        """Returns provider health status and latency."""
        pass
