"""
Master Integration Service for Project Astra OS.
Orchestrates GitHub, Gmail, Google Calendar, Notion, VS Code Workspace, and Smart Daily Briefing.
"""

from typing import Dict, List, Any, Optional
import time

from app.integrations.github.github_service import GitHubService
from app.integrations.gmail.gmail_service import GmailService
from app.integrations.calendar.calendar_service import CalendarService
from app.integrations.notion.notion_service import NotionService
from app.integrations.workspace.workspace_service import WorkspaceService


class IntegrationService:
    """
    Master Integration Platform Orchestrator.
    """

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        gmail_service: Optional[GmailService] = None,
        calendar_service: Optional[CalendarService] = None,
        notion_service: Optional[NotionService] = None,
        workspace_service: Optional[WorkspaceService] = None
    ):
        self.github = github_service or GitHubService()
        self.gmail = gmail_service or GmailService()
        self.calendar = calendar_service or CalendarService()
        self.notion = notion_service or NotionService()
        self.workspace = workspace_service or WorkspaceService()

    def generate_daily_briefing(self) -> Dict[str, Any]:
        """
        Generates Smart Daily Engineering Briefing summarizing GitHub PRs/issues, Gmail, Calendar, and Workspace priorities.
        """
        github_summary = self.github.get_repo_summary()
        inbox_threads = self.gmail.get_inbox_threads(limit=3)
        upcoming_events = self.calendar.get_upcoming_events()
        workspace_ctx = self.workspace.get_workspace_context()

        return {
            "timestamp": time.time(),
            "headline": "Good morning Rudra! Here is your Astra OS Engineering Briefing.",
            "github": {
                "active_repo": github_summary.get("repo_name"),
                "open_prs": github_summary.get("open_prs_count", 0),
                "open_issues": github_summary.get("open_issues_count", 0)
            },
            "gmail": {
                "inbox_unread": len(inbox_threads),
                "threads": inbox_threads
            },
            "calendar": {
                "upcoming_events_count": len(upcoming_events),
                "events": upcoming_events
            },
            "workspace": {
                "active_project": workspace_ctx.get("project_name"),
                "active_file": workspace_ctx.get("active_file")
            },
            "suggested_priorities": [
                "1. Review PR #42 for Milestone 6 Cloud Sync",
                "2. Prepare for Architecture Sync Meeting at 12:00 PM",
                "3. Continue Milestone 7 Real Integrations development"
            ]
        }
