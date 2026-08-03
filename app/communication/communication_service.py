"""
Communication Service Facade for Project Astra.
Unified Facade service for Email, Calendar, Notifications, Contacts, and Daily Briefings.
"""

from typing import Dict, Any, List, Optional
import time

from app.communication.email_service import EmailService
from app.communication.calendar_service import CalendarService
from app.communication.notification_service import NotificationService
from app.communication.contacts_service import ContactsService
from app.communication.message_router import MessageRouter
from app.models.email_message import EmailMessage
from app.models.calendar_event import CalendarEvent
from app.utils.logger import logger


class CommunicationService:
    """
    High-level facade interface for Astra's Communication & Productivity Platform.
    """

    def __init__(
        self,
        email_service: Optional[EmailService] = None,
        calendar_service: Optional[CalendarService] = None,
        notification_service: Optional[NotificationService] = None,
        contacts_service: Optional[ContactsService] = None
    ):
        self.email_service = email_service or EmailService()
        self.calendar_service = calendar_service or CalendarService()
        self.notification_service = notification_service or NotificationService()
        self.contacts_service = contacts_service or ContactsService()
        self.router = MessageRouter(
            email_service=self.email_service,
            notification_service=self.notification_service
        )

    def generate_daily_briefing(self) -> Dict[str, Any]:
        """
        Generates a consolidated morning briefing containing today's calendar events,
        unread emails, and system notifications.
        """
        now = time.time()
        end_of_day = now + 86400

        events = self.calendar_service.get_schedule(start_time=now, end_time=end_of_day)
        unread_emails = self.email_service.get_inbox(limit=5, unread_only=True)

        lines = [
            "🌅 **Project Astra Daily Briefing**",
            f"📅 **Today's Calendar Events ({len(events)}):**"
        ]

        for e in events:
            time_str = time.strftime("%H:%M", time.localtime(e.start_time))
            lines.append(f"  - `{time_str}`: {e.title} ({e.location or 'Online'})")

        lines.append(f"\n📩 **Unread Priority Emails ({len(unread_emails)}):**")
        for m in unread_emails:
            lines.append(f"  - **{m.sender}**: {m.subject}")

        briefing_text = "\n".join(lines)
        logger.info("[CommunicationService] Generated Daily Briefing.")

        return {
            "briefing_text": briefing_text,
            "events_count": len(events),
            "unread_emails_count": len(unread_emails)
        }
