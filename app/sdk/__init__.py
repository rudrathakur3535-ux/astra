"""
SDK Package for Project Astra.
Contains public plugin development interfaces (BasePlugin, PluginAPI, PluginHookManager, PluginEventBridge).
"""

from app.sdk.base_plugin import BasePlugin
from app.sdk.plugin_api import PluginAPI
from app.sdk.hooks import PluginHookManager
from app.sdk.events import PluginEventBridge

__all__ = [
    "BasePlugin",
    "PluginAPI",
    "PluginHookManager",
    "PluginEventBridge"
]
