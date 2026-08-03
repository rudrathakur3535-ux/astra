"""
Notification Model for Project Astra.
Represents system and workflow notification payloads.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    """
    Represents a system or workflow desktop notification.
    """
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    category: str = "general"
    is_delivered: bool = False
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "title": self.title,
            "message": self.message,
            "priority": self.priority.value if isinstance(self.priority, NotificationPriority) else self.priority,
            "category": self.category,
            "is_delivered": self.is_delivered,
            "created_at": self.created_at
        }
