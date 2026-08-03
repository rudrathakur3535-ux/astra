"""
Hooks Module for Project Astra SDK.
Manages inter-plugin hooks and filter callbacks.
"""

from typing import Dict, List, Callable, Any
from app.utils.logger import logger


class PluginHookManager:
    """
    Hook registration and execution manager.
    """

    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
        logger.debug(f"[HookManager] Registered hook for '{hook_name}'")

    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        results = []
        callbacks = self._hooks.get(hook_name, [])
        for cb in callbacks:
            try:
                res = cb(*args, **kwargs)
                results.append(res)
            except Exception as e:
                logger.error(f"[HookManager] Error executing hook '{hook_name}': {e}")
        return results
