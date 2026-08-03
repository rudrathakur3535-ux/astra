"""
Plugin Manager Facade for Project Astra.
Master coordinator managing plugin discovery, manifest validation, security sandboxing, loading, unloading, and hot-reload.
"""

import os
from typing import List, Dict, Any, Optional, Tuple

from app.models.plugin_info import PluginInfo, PluginStatus
from app.models.plugin_manifest import PluginManifest
from app.plugins.plugin_manifest import ManifestValidator
from app.plugins.plugin_sandbox import PluginSandbox
from app.plugins.plugin_loader import PluginLoader
from app.plugins.plugin_registry import PluginRegistry
from app.sdk.plugin_api import PluginAPI
from app.utils.logger import logger


class PluginManager:
    """
    Master Extension Platform Coordinator for Project Astra OS.
    """

    def __init__(self, plugins_dir: str = "app/plugins_installed"):
        self.plugins_dir = os.path.abspath(plugins_dir)
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.registry = PluginRegistry()
        self.sandbox = PluginSandbox()
        self.loader = PluginLoader()

    def discover_plugins(self) -> List[PluginInfo]:
        """
        Discovers all subdirectories in plugins_dir containing plugin.json or manifest.json.
        """
        discovered: List[PluginInfo] = []
        if not os.path.exists(self.plugins_dir):
            return []

        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)
            if os.path.isdir(item_path):
                manifest_file = os.path.join(item_path, "plugin.json")
                if not os.path.exists(manifest_file):
                    manifest_file = os.path.join(item_path, "manifest.json")

                if os.path.exists(manifest_file):
                    manifest, err = ManifestValidator.parse_and_validate(manifest_file)
                    if manifest:
                        info = PluginInfo(
                            name=manifest.name,
                            version=manifest.version,
                            author=manifest.author,
                            description=manifest.description,
                            entrypoint=manifest.entrypoint,
                            permissions=manifest.permissions,
                            install_path=item_path,
                            status=PluginStatus.DISCOVERED
                        )
                        self.registry.register_info(info)
                        discovered.append(info)
                    else:
                        logger.warning(f"[PluginManager] Invalid manifest in '{item_path}': {err}")

        logger.info(f"[PluginManager] Discovered {len(discovered)} plugins in '{self.plugins_dir}'")
        return discovered

    async def load_plugin(self, plugin_name: str, granted_permissions: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Loads a discovered plugin after verifying permissions.
        """
        info = self.registry.get_info(plugin_name)
        if not info:
            return False, f"Plugin '{plugin_name}' not found in registry."

        # 1. Verify Security Permissions
        ok, perms = self.sandbox.verify_permissions(info, granted_permissions=granted_permissions)
        if not ok:
            info.status = PluginStatus.PERMISSIONS_PENDING
            return False, f"Plugin '{plugin_name}' permissions not approved."

        # 2. Instantiate and Load Plugin
        api = PluginAPI(plugin_name=info.name)
        instance, err = self.loader.load_plugin(info, api)
        if not instance or err:
            info.status = PluginStatus.FAILED
            return False, err or "Failed to load plugin instance."

        # 3. Call Lifecycle on_load()
        try:
            loaded_ok = await instance.on_load()
            if not loaded_ok:
                info.status = PluginStatus.FAILED
                return False, f"Plugin '{plugin_name}' on_load() returned False."

            # Register Tools & Agents
            tools = await instance.register_tools()
            for tool in tools:
                api.register_tool(
                    name=tool.get("name", "tool"),
                    func=tool.get("func", lambda: None),
                    description=tool.get("description", "")
                )

            self.registry.register_instance(plugin_name, instance)
            logger.info(f"[PluginManager] Plugin '{plugin_name}' successfully LOADED.")
            return True, None

        except Exception as e:
            info.status = PluginStatus.FAILED
            logger.error(f"[PluginManager] Error loading plugin '{plugin_name}': {e}")
            return False, str(e)

    async def unload_plugin(self, plugin_name: str) -> Tuple[bool, Optional[str]]:
        """
        Unloads an active plugin cleanly.
        """
        instance = self.registry.get_instance(plugin_name)
        if not instance:
            return False, f"Plugin '{plugin_name}' is not currently loaded."

        try:
            await instance.on_unload()
            self.registry.unregister_instance(plugin_name)
            logger.info(f"[PluginManager] Plugin '{plugin_name}' UNLOADED successfully.")
            return True, None
        except Exception as e:
            logger.error(f"Error unloading plugin '{plugin_name}': {e}")
            return False, str(e)

    async def hot_reload_plugin(self, plugin_name: str, granted_permissions: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Hot-reloads an active plugin dynamically without restarting Astra OS.
        """
        logger.info(f"[PluginManager] Hot-reloading plugin '{plugin_name}'...")
        if self.registry.get_instance(plugin_name):
            await self.unload_plugin(plugin_name)

        return await self.load_plugin(plugin_name, granted_permissions=granted_permissions)
