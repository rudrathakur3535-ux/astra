"""
Comprehensive Unit & Integration Test Suite for Real Integrations & AI Workspace Platform.
"""

import pytest
import time
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.repository_context import RepositoryContext, PullRequestDiff
from app.models.email_thread import EmailThread, EmailMessage
from app.models.calendar_context import CalendarEvent, ScheduleConflictReport
from app.models.workspace_context import WorkspaceContext

from app.integrations.github.github_service import GitHubService
from app.integrations.github.pull_request_service import PullRequestService
from app.integrations.gmail.gmail_service import GmailService
from app.integrations.gmail.mail_indexer import MailIndexer
from app.integrations.calendar.calendar_service import CalendarService
from app.integrations.calendar.availability_engine import AvailabilityEngine
from app.integrations.notion.notion_service import NotionService
from app.integrations.workspace.workspace_service import WorkspaceService

from app.services.integration_service import IntegrationService
from app.api.integrations_api import router as integrations_router


class TestGitHubIntegration:
    """Tests GitHub repository, PR review, and issue services."""

    def test_pr_code_review_service(self):
        pr_service = PullRequestService()
        pr = PullRequestDiff(
            pr_id=1,
            title="Update Auth Policy",
            author="dev",
            branch="feature/auth",
            changed_files=["app/security/authentication.py"],
            diff_text="+ constant_time_compare"
        )
        review = pr_service.review_pull_request(pr)
        assert review["pr_id"] == 1
        assert len(review["comments"]) >= 1

    def test_github_service_repo_summary(self):
        gh_service = GitHubService()
        summary = gh_service.get_repo_summary("rudrathakur", "astra-os")
        assert summary["repo_name"] == "astra-os"


class TestGmailIntegration:
    """Tests Gmail inbox, indexing, priority detection, and drafting."""

    def test_priority_detection(self):
        indexer = MailIndexer()
        assert indexer.detect_priority("Urgent Meeting", "Body") == "high"
        assert indexer.detect_priority("Regular Update", "Body") == "normal"

    def test_gmail_service_drafting(self):
        svc = GmailService()
        threads = svc.get_inbox_threads()
        assert len(threads) >= 1

        draft = svc.draft_email_reply("t-1", "user@test.com", "Project Status", "Draft reply prompt")
        assert draft["status"] == "drafted"
        assert "Re: Project Status" in draft["subject"]


class TestCalendarIntegration:
    """Tests Calendar event scheduling, availability engine, and conflict detection."""

    def test_conflict_detection(self):
        engine = AvailabilityEngine()
        existing = [
            CalendarEvent("e1", "Sync", start_time=100.0, end_time=200.0)
        ]

        report_conflict = engine.detect_conflicts(new_start=150.0, new_end=250.0, existing_events=existing)
        assert report_conflict.has_conflict is True
        assert len(report_conflict.suggested_slots) == 1

        report_clear = engine.detect_conflicts(new_start=300.0, new_end=400.0, existing_events=existing)
        assert report_clear.has_conflict is False

    def test_calendar_service_scheduling(self):
        svc = CalendarService()
        now = time.time() + 86400  # Tomorrow
        res = svc.schedule_event("Team Standup", start_time=now, duration_hours=1.0)
        assert res["status"] == "scheduled"


class TestNotionAndWorkspaceIntegration:
    """Tests Notion page indexing and VS Code workspace context engine."""

    def test_notion_service(self):
        svc = NotionService()
        created = svc.create_page("Astra Architecture", "Details on Milestone 7.")
        assert created["page_id"].startswith("notion-")

        results = svc.search_workspace("Architecture")
        assert len(results) >= 1

    def test_workspace_service(self):
        svc = WorkspaceService()
        ctx = svc.get_workspace_context()
        assert ctx["project_name"] == "astra"
        assert len(ctx["open_files"]) >= 1

        query_res = svc.query_workspace_architecture("authentication")
        assert "authentication.py" in str(query_res["matched_components"])


class TestMasterIntegrationService:
    """Tests master integration orchestrator and Smart Daily Briefing."""

    def test_daily_briefing_generation(self):
        master = IntegrationService()
        brief = master.generate_daily_briefing()

        assert "Astra OS Engineering Briefing" in brief["headline"]
        assert "github" in brief
        assert "gmail" in brief
        assert "calendar" in brief
        assert "workspace" in brief
        assert len(brief["suggested_priorities"]) >= 1


class TestIntegrationsAPIEndpoints:
    """Tests FastAPI Integrations Router REST endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(integrations_router)
        self.client = TestClient(self.app)

    def test_daily_brief_endpoint(self):
        res = self.client.get("/api/integrations/daily-brief")
        assert res.status_code == 200
        assert "headline" in res.json()

    def test_github_endpoints(self):
        res_sum = self.client.get("/api/integrations/github/summary")
        assert res_sum.status_code == 200

        res_rev = self.client.get("/api/integrations/github/review")
        assert res_rev.status_code == 200
        assert res_rev.json()["status"] == "reviewed"

    def test_gmail_endpoints(self):
        res_inbox = self.client.get("/api/integrations/gmail/inbox")
        assert res_inbox.status_code == 200

        res_draft = self.client.post("/api/integrations/gmail/draft", json={
            "thread_id": "t-1",
            "recipient": "dev@test.com",
            "subject": "Review",
            "body_prompt": "Looks good"
        })
        assert res_draft.status_code == 200
        assert res_draft.json()["status"] == "drafted"

    def test_calendar_endpoints(self):
        res_events = self.client.get("/api/integrations/calendar/events")
        assert res_events.status_code == 200

        res_sched = self.client.post("/api/integrations/calendar/schedule", json={
            "summary": "DSA Practice",
            "start_time": time.time() + 100000,
            "duration_hours": 2.0
        })
        assert res_sched.status_code == 200
        assert res_sched.json()["status"] == "scheduled"

    def test_workspace_endpoint(self):
        res = self.client.get("/api/integrations/workspace/context")
        assert res.status_code == 200
        assert "project_name" in res.json()
