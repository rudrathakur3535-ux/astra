"""
Event Bus Module for Project Astra.
Provides event-driven PubSub communication between decoupled specialist agents.
"""

from typing import Dict, List, Callable, Any
from app.utils.logger import logger


class EventBus:
    """
    Publish-Subscribe Event Bus for multi-agent event dispatching.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[str, Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[str, Any], None]) -> None:
        """
        Subscribes a callback handler to an event topic.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"[EventBus] Subscribed callback to event '{event_type}'")

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publishes an event topic to all registered subscribers.
        """
        subscribers = self._subscribers.get(event_type, [])
        logger.info(f"[EventBus] Event '{event_type}' published to {len(subscribers)} subscribers.")
        for callback in subscribers:
            try:
                callback(event_type, data)
            except Exception as e:
                logger.error(f"[EventBus] Error executing subscriber for '{event_type}': {e}", exc_info=True)


# Global default EventBus singleton
event_bus = EventBus()
