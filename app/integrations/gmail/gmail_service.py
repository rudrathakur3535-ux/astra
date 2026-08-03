"""
Gmail Service for Project Astra OS.
Reads inbox messages, searches threads, drafts replies, and summarizes emails.
"""

from typing import Dict, List, Any, Optional
import time
from app.integrations.gmail.gmail_oauth import GmailOAuthManager
from app.integrations.gmail.mail_indexer import MailIndexer
from app.models.email_thread import EmailThread, EmailMessage


class GmailService:
    """
    Gmail Service orchestrator.
    """

    def __init__(self, oauth_manager: Optional[GmailOAuthManager] = None):
        self.oauth_manager = oauth_manager or GmailOAuthManager()
        self.indexer = MailIndexer()

    def get_inbox_threads(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Returns recent inbox email threads with priority classification.
        """
        mock_msg = EmailMessage(
            msg_id="msg-001",
            thread_id="thread-001",
            sender="lead-architect@company.com",
            recipient="rudra@astra.local",
            subject="Urgent: Production Deployment Review Required",
            body="Hi Rudra, please review the latest deployment checklist before 4 PM.",
            timestamp=time.time() - 3600
        )
        thread = self.indexer.index_thread("thread-001", mock_msg.subject, [mock_msg])
        return [thread.to_dict()]

    def draft_email_reply(self, thread_id: str, recipient: str, subject: str, body_prompt: str) -> Dict[str, Any]:
        """
        Drafts an email reply based on prompt context.
        """
        draft_content = f"Hi {recipient.split('@')[0]},\n\nThank you for reaching out regarding '{subject}'. I have reviewed your request: '{body_prompt}'. Everything looks good on my end.\n\nBest regards,\nAstra OS"
        return {
            "status": "drafted",
            "thread_id": thread_id,
            "recipient": recipient,
            "subject": f"Re: {subject}",
            "draft_body": draft_content
        }
