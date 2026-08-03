"""
Notification Adapter for Project Astra.
Dispatches system and workflow toast notifications.
"""

from typing import List
from app.models.notification import Notification
from app.utils.logger import logger


class NotificationAdapter:
    """
    Desktop notification provider.
    """

    def __init__(self):
        self._sent_notifications: List[Notification] = []

    def send_notification(self, notification: Notification) -> bool:
        """
        Dispatches system toast notification.
        """
        notification.is_delivered = True
        self._sent_notifications.append(notification)
        logger.info(f"[NotificationAdapter] 🔔 TOAST NOTIFICATION: [{notification.priority.value.upper()}] {notification.title} - {notification.message}")
        return True

    def list_delivered(self) -> List[Notification]:
        return list(self._sent_notifications)
