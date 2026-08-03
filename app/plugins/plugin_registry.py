"""
Plugin Registry Module for Project Astra.
Central registry tracking discovered, loaded, and unloaded plugin instances.
"""

from typing import Dict, List, Optional, Any
from app.models.plugin_info import PluginInfo, PluginStatus
from app.sdk.base_plugin import BasePlugin
from app.utils.logger import logger


class PluginRegistry:
    """
    Registry maintaining active and historical plugin instances.
    """

    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._instances: Dict[str, BasePlugin] = {}

    def register_info(self, info: PluginInfo) -> None:
        self._plugins[info.name] = info

    def register_instance(self, name: str, instance: BasePlugin) -> None:
        self._instances[name] = instance
        if name in self._plugins:
            self._plugins[name].status = PluginStatus.LOADED

    def unregister_instance(self, name: str) -> bool:
        if name in self._instances:
            del self._instances[name]
        if name in self._plugins:
            self._plugins[name].status = PluginStatus.UNLOADED
        return True

    def get_info(self, name: str) -> Optional[PluginInfo]:
        return self._plugins.get(name)

    def get_instance(self, name: str) -> Optional[BasePlugin]:
        return self._instances.get(name)

    def list_loaded_plugins(self) -> List[PluginInfo]:
        return [info for info in self._plugins.values() if info.status == PluginStatus.LOADED]

    def list_all_plugins(self) -> List[PluginInfo]:
        return list(self._plugins.values())
