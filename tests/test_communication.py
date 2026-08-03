"""
Unit tests for Day 12 Communication & Productivity Platform.
Tests EmailService, CalendarService, NotificationService, ContactsService, MessageRouter,
and CommunicationService Daily Briefing.
"""

import pytest
import time
from typing import List

from app.models.email_message import EmailMessage
from app.models.calendar_event import CalendarEvent
from app.models.notification import Notification, NotificationPriority
from app.models.contact import Contact
from app.adapters.gmail_adapter import GmailAdapter
from app.adapters.calendar_adapter import CalendarAdapter
from app.adapters.notification_adapter import NotificationAdapter
from app.communication.email_service import EmailService
from app.communication.calendar_service import CalendarService
from app.communication.notification_service import NotificationService
from app.communication.contacts_service import ContactsService
from app.communication.message_router import MessageRouter
from app.communication.communication_service import CommunicationService
from app.security.permissions import PermissionManager, permission_manager


class TestEmailServiceAndDrafting:
    def test_inbox_retrieval_and_drafting(self):
        service = EmailService()
        inbox = service.get_inbox(limit=10)
        assert len(inbox) >= 2

        original = inbox[0]
        draft = service.draft_reply(original, reply_body="I reviewed the runtime state. Everything is passing.")

        assert draft.recipients == [original.sender]
        assert draft.subject == f"Re: {original.subject}"
        assert "draft" in draft.tags

    def test_email_search(self):
        service = EmailService()
        results = service.search_emails("Architecture")
        assert len(results) >= 1
        assert "Architecture" in results[0].subject


class TestCalendarServiceAndConflicts:
    def test_schedule_retrieval(self):
        service = CalendarService()
        events = service.get_schedule()
        assert len(events) >= 1

    def test_conflict_detection(self):
        service = CalendarService()
        now = time.time()

        # Create an event overlapping with demo event 1 (now + 3600 to now + 7200)
        conflicting_event = CalendarEvent(
            title="Overlapping Meeting",
            start_time=now + 4000,
            end_time=now + 5000
        )

        conflicts = service.detect_conflicts(conflicting_event)
        assert len(conflicts) >= 1
        assert conflicts[0].title == "Astra Engineering Standup"

        success, conflict_list = service.schedule_event(conflicting_event, allow_conflicts=False)
        assert success is False
        assert len(conflict_list) >= 1


class TestNotificationsAndContacts:
    def test_notification_dispatch(self):
        adapter = NotificationAdapter()
        service = NotificationService(adapter=adapter)

        success = service.notify("Workflow Complete", "Workflow wf_123 finished successfully.", priority=NotificationPriority.HIGH)
        assert success is True
        assert len(adapter.list_delivered()) == 1

    def test_contacts_lookup(self):
        service = ContactsService()
        contact = service.get_contact_by_email("alex@astra.os")
        assert contact is not None
        assert contact.name == "Alex Rivera"

        search_res = service.search_contacts("Rudra")
        assert len(search_res) >= 1


class TestMessageRouterAndPermissions:
    def test_message_router_approval_enforcement(self):
        router = MessageRouter()
        email = EmailMessage(
            sender="rudra@astra.os",
            recipients=["external@client.com"],
            subject="Status Update",
            body="Project is on schedule."
        )

        # Without user approval, should require approval
        res1 = router.send_external_email(email, user_approved=False)
        assert res1["success"] is False
        assert "approval" in res1["reason"].lower()

        # With user approval, should succeed
        res2 = router.send_external_email(email, user_approved=True)
        assert res2["success"] is True


class TestCommunicationServiceFacade:
    def test_daily_briefing_generation(self):
        service = CommunicationService()
        briefing = service.generate_daily_briefing()

        assert "briefing_text" in briefing
        assert "Daily Briefing" in briefing["briefing_text"]
        assert briefing["events_count"] >= 1
