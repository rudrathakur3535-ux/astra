"""
Plugin Context Module for Project Astra.
Encapsulates runtime state and config data passed to isolated plugin instances.
"""

from typing import Dict, Any, Optional
from app.models.plugin_info import PluginInfo


class PluginContext:
    """
    Execution context provided to plugins.
    """

    def __init__(self, info: PluginInfo, global_config: Optional[Dict[str, Any]] = None):
        self.info = info
        self.config = info.config
        self.global_config = global_config or {}
        self.store: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.store[key] = value
