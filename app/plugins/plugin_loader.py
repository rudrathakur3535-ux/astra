"""
Plugin Loader Module for Project Astra.
Dynamically imports Python plugin modules and manages lifecycle calls.
"""

import importlib.util
import os
import sys
from typing import Tuple, Optional, Any, Type
from app.models.plugin_info import PluginInfo
from app.sdk.base_plugin import BasePlugin
from app.sdk.plugin_api import PluginAPI
from app.utils.logger import logger


class PluginLoader:
    """
    Dynamic Python module loader for third-party plugins.
    """

    def load_plugin(self, info: PluginInfo, api: PluginAPI) -> Tuple[Optional[BasePlugin], Optional[str]]:
        """
        Dynamically imports entrypoint module and instantiates BasePlugin subclass.

        Returns:
            Tuple[Optional[BasePlugin], Optional[str]]: (plugin_instance, error_message)
        """
        entrypoint_path = os.path.join(info.install_path, info.entrypoint)
        if not os.path.exists(entrypoint_path):
            return None, f"Plugin entrypoint file not found: {entrypoint_path}"

        module_name = f"astra_plugin_{info.name.replace(' ', '_').lower()}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, entrypoint_path)
            if not spec or not spec.loader:
                return None, f"Failed to create module spec for '{entrypoint_path}'"

            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)

            # Find subclass of BasePlugin
            plugin_cls: Optional[Type[BasePlugin]] = None
            for attr in dir(mod):
                val = getattr(mod, attr)
                if isinstance(val, type) and issubclass(val, BasePlugin) and val is not BasePlugin:
                    plugin_cls = val
                    break

            if not plugin_cls:
                return None, f"No BasePlugin subclass found in entrypoint '{info.entrypoint}'"

            instance = plugin_cls(name=info.name, version=info.version)
            instance.initialize_api(api)
            logger.info(f"[PluginLoader] Loaded plugin instance '{instance.name}' (v{instance.version})")
            return instance, None

        except Exception as e:
            err = f"Error importing plugin '{info.name}': {e}"
            logger.error(err)
            return None, err
