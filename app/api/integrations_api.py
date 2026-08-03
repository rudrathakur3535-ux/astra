"""
FastAPI Router for External Integrations & Workspace Platform in Project Astra OS.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.integration_service import IntegrationService

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

_integration_service_instance: Optional[IntegrationService] = None


def get_integration_service() -> IntegrationService:
    global _integration_service_instance
    if _integration_service_instance is None:
        _integration_service_instance = IntegrationService()
    return _integration_service_instance


class EmailDraftRequest(BaseModel):
    thread_id: str
    recipient: str
    subject: str
    body_prompt: str


class EventScheduleRequest(BaseModel):
    summary: str
    start_time: float
    duration_hours: float = 1.0


class NotionPageRequest(BaseModel):
    title: str
    content: str


@router.get("/daily-brief", response_class=JSONResponse)
async def get_daily_briefing():
    """Returns Smart Daily Engineering Briefing."""
    svc = get_integration_service()
    return svc.generate_daily_briefing()


@router.get("/github/summary", response_class=JSONResponse)
async def get_github_summary(owner: str = "rudrathakur", repo: str = "astra-os"):
    """Returns GitHub repository summary context."""
    svc = get_integration_service()
    return svc.github.get_repo_summary(owner, repo)


@router.get("/github/review", response_class=JSONResponse)
async def review_github_pr(owner: str = "rudrathakur", repo: str = "astra-os"):
    """Triggers automated Pull Request review assistant."""
    svc = get_integration_service()
    return svc.github.review_latest_pr(owner, repo)


@router.get("/gmail/inbox", response_class=JSONResponse)
async def get_gmail_inbox(limit: int = 5):
    """Returns recent Gmail inbox threads."""
    svc = get_integration_service()
    return {"threads": svc.gmail.get_inbox_threads(limit=limit)}


@router.post("/gmail/draft", response_class=JSONResponse)
async def draft_gmail_reply(req: EmailDraftRequest):
    """Drafts an email reply."""
    svc = get_integration_service()
    return svc.gmail.draft_email_reply(req.thread_id, req.recipient, req.subject, req.body_prompt)


@router.get("/calendar/events", response_class=JSONResponse)
async def get_calendar_events():
    """Returns upcoming Google Calendar events."""
    svc = get_integration_service()
    return {"events": svc.calendar.get_upcoming_events()}


@router.post("/calendar/schedule", response_class=JSONResponse)
async def schedule_calendar_event(req: EventScheduleRequest):
    """Schedules a new meeting after verifying no conflicts exist."""
    svc = get_integration_service()
    return svc.calendar.schedule_event(req.summary, req.start_time, req.duration_hours)


@router.get("/notion/pages", response_class=JSONResponse)
async def search_notion_pages(query: str = ""):
    """Searches Notion workspace pages."""
    svc = get_integration_service()
    return {"pages": svc.notion.search_workspace(query)}


@router.post("/notion/create", response_class=JSONResponse)
async def create_notion_page(req: NotionPageRequest):
    """Creates a new Notion page entry."""
    svc = get_integration_service()
    return svc.notion.create_page(req.title, req.content)


@router.get("/workspace/context", response_class=JSONResponse)
async def get_workspace_context(root_dir: str = "c:/Users/rudra/OneDrive/Desktop/astra"):
    """Returns full VS Code workspace context, open files, and AST dependency graph."""
    svc = get_integration_service()
    return svc.workspace.get_workspace_context(root_dir)
