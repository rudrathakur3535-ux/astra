"""
Plugin API Module for Project Astra SDK.
Controlled public API surface exposed to third-party plugins.
"""

from typing import Dict, Any, Optional, Callable
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.tools.tool_registry import tool_registry, ToolRegistry
from app.orchestrator.event_bus import event_bus, EventBus
from app.utils.logger import logger


class DynamicPluginTool(BaseTool):
    """
    Dynamic wrapper creating BaseTool instances for plugin-registered functions.
    """

    def __init__(self, tool_name: str, func: Callable, desc: str, params: Optional[Dict[str, Any]] = None):
        self._name = tool_name
        self._func = func
        self._desc = desc
        self._params = params or {"type": "object", "properties": {}}

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._desc

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return self._params

    def execute(self, **kwargs) -> ToolResponse:
        try:
            res = self._func(**kwargs)
            return ToolResponse(success=True, data=res)
        except Exception as e:
            return ToolResponse(success=False, error_message=str(e))


class PluginAPI:
    """
    Controlled API gateway providing access to Astra OS services.
    """

    def __init__(
        self,
        plugin_name: str,
        registry: Optional[ToolRegistry] = None,
        bus: Optional[EventBus] = None
    ):
        self.plugin_name = plugin_name
        self.tool_registry = registry or tool_registry
        self.event_bus = bus or event_bus

    def register_tool(self, name: str, func: Callable, description: str, parameters: Optional[Dict[str, Any]] = None) -> bool:
        """Registers a tool on behalf of the plugin."""
        tool_name = f"{self.plugin_name}.{name}" if not name.startswith(self.plugin_name) else name
        plugin_tool = DynamicPluginTool(tool_name=tool_name, func=func, desc=description, params=parameters)
        self.tool_registry.register(plugin_tool)
        logger.info(f"[PluginAPI:{self.plugin_name}] Registered tool '{tool_name}'")
        return True

    def publish_event(self, topic: str, payload: Any) -> None:
        """Publishes an event to Astra's EventBus."""
        self.event_bus.publish(topic, payload)

    def subscribe_event(self, topic: str, callback: Callable[[str, Any], None]) -> None:
        """Subscribes to an event topic on Astra's EventBus."""
        self.event_bus.subscribe(topic, callback)
