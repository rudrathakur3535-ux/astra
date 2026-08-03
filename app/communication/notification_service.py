"""
Notification Service Module for Project Astra.
Manages desktop system notifications and workflow completion alerts.
"""

from typing import List, Optional
from app.adapters.notification_adapter import NotificationAdapter
from app.models.notification import Notification, NotificationPriority
from app.utils.logger import logger


class NotificationService:
    """
    Notification service managing alert notifications.
    """

    def __init__(self, adapter: Optional[NotificationAdapter] = None):
        self.adapter = adapter or NotificationAdapter()

    def notify(
        self,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        category: str = "general"
    ) -> bool:
        """
        Dispatches a system notification.
        """
        notif = Notification(
            title=title,
            message=message,
            priority=priority,
            category=category
        )
        return self.adapter.send_notification(notif)
