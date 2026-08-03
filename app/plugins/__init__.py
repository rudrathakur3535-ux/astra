"""
Plugins Package for Project Astra.
Extension Platform featuring PluginManager, PluginLoader, PluginRegistry, ManifestValidator, PluginSandbox, and PluginContext.
"""

from app.plugins.plugin_manager import PluginManager
from app.plugins.plugin_manifest import ManifestValidator
from app.plugins.plugin_loader import PluginLoader
from app.plugins.plugin_registry import PluginRegistry
from app.plugins.plugin_sandbox import PluginSandbox
from app.plugins.plugin_context import PluginContext

__all__ = [
    "PluginManager",
    "ManifestValidator",
    "PluginLoader",
    "PluginRegistry",
    "PluginSandbox",
    "PluginContext"
]
