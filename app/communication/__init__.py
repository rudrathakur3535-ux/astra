"""
Communication Package for Project Astra.
Communication & Productivity Platform featuring Email, Calendar, Desktop Notifications, Contacts Directory, Message Router, and Daily Briefings.
"""

from app.communication.communication_service import CommunicationService
from app.communication.email_service import EmailService
from app.communication.calendar_service import CalendarService
from app.communication.notification_service import NotificationService
from app.communication.contacts_service import ContactsService
from app.communication.message_router import MessageRouter

__all__ = [
    "CommunicationService",
    "EmailService",
    "CalendarService",
    "NotificationService",
    "ContactsService",
    "MessageRouter"
]
