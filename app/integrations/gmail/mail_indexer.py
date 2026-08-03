"""
Gmail Mail Indexer & Priority Detector for Project Astra OS.
Indexes email threads and detects priority messages.
"""

from typing import Dict, List, Any, Optional
from app.models.email_thread import EmailThread, EmailMessage


class MailIndexer:
    """
    Indexes email messages and evaluates priority scores.
    """

    HIGH_PRIORITY_KEYWORDS = ["urgent", "action required", "meeting", "deploy", "security alert", "critical"]

    def detect_priority(self, subject: str, body: str) -> str:
        """Determines email priority."""
        text = f"{subject} {body}".lower()
        if any(kw in text for kw in self.HIGH_PRIORITY_KEYWORDS):
            return "high"
        return "normal"

    def index_thread(self, thread_id: str, subject: str, messages: List[EmailMessage]) -> EmailThread:
        """Indexes thread and computes summary."""
        priority = "normal"
        if messages:
            priority = self.detect_priority(subject, messages[0].body)

        summary = f"Thread contains {len(messages)} messages regarding '{subject}'."
        return EmailThread(
            thread_id=thread_id,
            subject=subject,
            messages=messages,
            priority=priority,
            summary=summary
        )
