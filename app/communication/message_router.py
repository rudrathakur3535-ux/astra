"""
Message Router Module for Project Astra.
Routes communication dispatches and enforces PermissionLayer user approval on external dispatches.
"""

from typing import Dict, Any, Optional
from app.models.email_message import EmailMessage
from app.security.permissions import PermissionManager, permission_manager
from app.communication.email_service import EmailService
from app.communication.notification_service import NotificationService
from app.utils.logger import logger


class MessageRouter:
    """
    Message router verifying permissions before dispatching external communications.
    """

    def __init__(
        self,
        permission_manager: Optional[PermissionManager] = None,
        email_service: Optional[EmailService] = None,
        notification_service: Optional[NotificationService] = None
    ):
        self.permission_manager = permission_manager or permission_manager
        self.email_service = email_service or EmailService()
        self.notification_service = notification_service or NotificationService()

    def send_external_email(self, email: EmailMessage, user_approved: bool = False) -> Dict[str, Any]:
        """
        Enforces permission check before dispatching an email.
        """
        if not user_approved:
            logger.warning(f"[MessageRouter] Email dispatch REQUIRES_APPROVAL. Awaiting user consent.")
            return {"success": False, "reason": "User approval required for external email dispatch."}

        # Dispatch email
        dispatched = self.email_service.send_email(email)
        return {"success": dispatched, "message_id": email.message_id}
