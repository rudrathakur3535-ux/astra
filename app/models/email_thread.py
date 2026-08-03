"""
Email Thread Model for Project Astra OS.
Represents Gmail threads, messages, drafts, and priority ratings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class EmailMessage:
    msg_id: str
    thread_id: str
    sender: str
    recipient: str
    subject: str
    body: str
    is_read: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class EmailThread:
    thread_id: str
    subject: str
    messages: List[EmailMessage] = field(default_factory=list)
    priority: str = "normal"  # high, normal, low
    summary: str = ""
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "subject": self.subject,
            "message_count": len(self.messages),
            "priority": self.priority,
            "summary": self.summary,
            "updated_at": self.updated_at
        }
