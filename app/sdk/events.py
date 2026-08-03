"""
Events Bridge Module for Project Astra SDK.
Bridges plugin event subscriptions with Astra's core EventBus.
"""

from typing import Callable, Any, Dict, Optional
from app.models.plugin_event import PluginEvent
from app.orchestrator.event_bus import event_bus, EventBus
from app.utils.logger import logger


class PluginEventBridge:
    """
    Event bridge forwarding events between plugins and Astra OS.
    """

    def __init__(self, bus: Optional[EventBus] = None):
        self.bus = bus or event_bus

    def emit_plugin_event(self, event: PluginEvent) -> None:
        topic = f"plugin.{event.plugin_name}.{event.event_type}"
        self.bus.publish(topic, event.to_dict())

    def subscribe_plugin_event(self, topic: str, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        self.bus.subscribe(topic, handler)
