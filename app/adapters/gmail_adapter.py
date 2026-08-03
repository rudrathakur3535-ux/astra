"""
Gmail / Email Adapter for Project Astra.
Provides mock and SMTP/IMAP email reading, drafting, and dispatch capabilities.
"""

from typing import List, Optional, Dict, Any
import time

from app.models.email_message import EmailMessage
from app.utils.logger import logger


class GmailAdapter:
    """
    Email provider adapter managing email inbox reading, searching, and sending.
    """

    def __init__(self):
        self._inbox: List[EmailMessage] = []
        self._sent_box: List[EmailMessage] = []
        self._populate_demo_inbox()

    def _populate_demo_inbox(self) -> None:
        """Populates demo email inbox messages."""
        self._inbox.append(EmailMessage(
            sender="alex@astra.os",
            recipients=["rudra@astra.os"],
            subject="Project Astra Architecture Review",
            body="Hi Rudra, The Day 11 Autonomous Execution Runtime looks outstanding!",
            snippet="The Day 11 Autonomous Execution Runtime looks outstanding!",
            is_read=False,
            tags=["important", "review"]
        ))
        self._inbox.append(EmailMessage(
            sender="team@github.com",
            recipients=["rudra@astra.os"],
            subject="Security Alert: Dependency update available",
            body="A new security update is available for sentence-transformers in your repository.",
            snippet="A new security update is available for sentence-transformers...",
            is_read=True,
            tags=["security"]
        ))

    def list_emails(self, limit: int = 10, unread_only: bool = False) -> List[EmailMessage]:
        emails = [e for e in self._inbox if not unread_only or not e.is_read]
        return emails[:limit]

    def send_email(self, message: EmailMessage) -> bool:
        self._sent_box.append(message)
        logger.info(f"[GmailAdapter] Dispatched email to {', '.join(message.recipients)} with subject '{message.subject}'")
        return True

    def search_emails(self, query: str) -> List[EmailMessage]:
        query_lower = query.lower()
        results = [
            e for e in self._inbox
            if query_lower in e.subject.lower() or query_lower in e.body.lower() or query_lower in e.sender.lower()
        ]
        return results
