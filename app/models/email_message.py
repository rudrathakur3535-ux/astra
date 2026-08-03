"""
Email Message Model for Project Astra.
Encapsulates email messages, headers, recipients, snippets, and threads.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import uuid


@dataclass
class EmailMessage:
    """
    Represents an email message in Astra's Communication Platform.
    """
    sender: str
    recipients: List[str]
    subject: str
    body: str
    snippet: str = ""
    is_read: bool = False
    thread_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipients": self.recipients,
            "subject": self.subject,
            "body": self.body,
            "snippet": self.snippet or self.body[:100],
            "is_read": self.is_read,
            "thread_id": self.thread_id,
            "tags": self.tags,
            "timestamp": self.timestamp
        }
