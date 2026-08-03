"""
Communication Port Interface for Project Astra (Hexagonal Architecture).
Decouples core business logic from external email, calendar, and notification providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.email_message import EmailMessage
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification
from app.models.contact import Contact


class CommunicationPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Communication & Productivity Adapters.
    """

    # Email operations
    @abstractmethod
    def list_emails(self, limit: int = 10) -> List[EmailMessage]:
        """Lists recent email messages."""
        pass

    @abstractmethod
    def send_email(self, message: EmailMessage) -> bool:
        """Dispatches an email message to recipients."""
        pass

    # Calendar operations
    @abstractmethod
    def list_events(self, start_time: float, end_time: float) -> List[CalendarEvent]:
        """Lists calendar events within a given timeframe."""
        pass

    @abstractmethod
    def create_event(self, event: CalendarEvent) -> bool:
        """Creates a new calendar event."""
        pass

    # Notification operations
    @abstractmethod
    def send_notification(self, notification: Notification) -> bool:
        """Displays or delivers a system desktop notification."""
        pass

    # Contact operations
    @abstractmethod
    def list_contacts(self) -> List[Contact]:
        """Lists all address book contacts."""
        pass

    @abstractmethod
    def save_contact(self, contact: Contact) -> bool:
        """Saves or updates a contact entry."""
        pass
