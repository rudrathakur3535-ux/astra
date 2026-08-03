"""
Email Service Module for Project Astra.
Manages inbox reading, searching, drafting replies, and thread summarization.
"""

from typing import List, Optional, Dict, Any
from app.adapters.gmail_adapter import GmailAdapter
from app.models.email_message import EmailMessage
from app.utils.logger import logger


class EmailService:
    """
    Email service managing email operations and draft generation.
    """

    def __init__(self, adapter: Optional[GmailAdapter] = None):
        self.adapter = adapter or GmailAdapter()

    def get_inbox(self, limit: int = 10, unread_only: bool = False) -> List[EmailMessage]:
        return self.adapter.list_emails(limit=limit, unread_only=unread_only)

    def search_emails(self, query: str) -> List[EmailMessage]:
        return self.adapter.search_emails(query)

    def draft_reply(self, original_email: EmailMessage, reply_body: str) -> EmailMessage:
        """
        Creates an unsent draft EmailMessage in response to an original message.
        """
        draft = EmailMessage(
            sender="rudra@astra.os",
            recipients=[original_email.sender],
            subject=f"Re: {original_email.subject}",
            body=reply_body,
            thread_id=original_email.thread_id or original_email.message_id,
            tags=["draft"]
        )
        logger.info(f"[EmailService] Created email draft for '{original_email.sender}' with subject '{draft.subject}'")
        return draft

    def send_email(self, message: EmailMessage) -> bool:
        """Dispatches an email through adapter."""
        return self.adapter.send_email(message)
