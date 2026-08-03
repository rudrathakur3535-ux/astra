"""
Base Plugin Abstract Class for Project Astra SDK.
Abstract base class that all third-party plugins must inherit.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.utils.logger import logger


class BasePlugin(ABC):
    """
    Abstract Base Class defining Astra Plugin lifecycle and extension contracts.
    """

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.api: Optional[Any] = None

    def initialize_api(self, api: Any) -> None:
        """Injects SDK API interface into the plugin instance."""
        self.api = api

    @abstractmethod
    async def on_load(self) -> bool:
        """Lifecycle hook triggered when plugin is loaded."""
        pass

    async def register_tools(self) -> List[Dict[str, Any]]:
        """Optional hook to register tools. Returns list of tool definition dicts."""
        return []

    async def register_agents(self) -> List[Any]:
        """Optional hook to register specialist agents."""
        return []

    @abstractmethod
    async def on_unload(self) -> bool:
        """Lifecycle hook triggered when plugin is unloaded."""
        pass
