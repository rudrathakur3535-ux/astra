"""
Plugin Port Interface for Project Astra (Hexagonal Architecture).
Decouples core plugin management from storage and execution environments.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.plugin_info import PluginInfo
from app.models.plugin_manifest import PluginManifest


class PluginPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Plugin Extension Adapters.
    """

    @abstractmethod
    def discover_plugins(self, plugins_dir: str) -> List[PluginInfo]:
        """Discovers plugin directories containing manifest files."""
        pass

    @abstractmethod
    def load_manifest(self, manifest_path: str) -> Optional[PluginManifest]:
        """Loads and parses a plugin manifest file."""
        pass

    @abstractmethod
    def save_plugin_info(self, info: PluginInfo) -> bool:
        """Persists plugin state info."""
        pass

    @abstractmethod
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Retrieves plugin state info by name."""
        pass
