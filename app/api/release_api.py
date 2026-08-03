"""
FastAPI Router for Astra OS v1.0 Release Candidate & Productization.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.release_service import ReleaseService

router = APIRouter(prefix="/api/v1/release", tags=["release_v1"])

_release_service_instance: Optional[ReleaseService] = None


def get_release_service() -> ReleaseService:
    global _release_service_instance
    if _release_service_instance is None:
        _release_service_instance = ReleaseService()
    return _release_service_instance


class OnboardingRequest(BaseModel):
    username: str
    primary_provider: str = "gemini"
    theme: str = "dark_glassmorphism"


class DemoRunRequest(BaseModel):
    scenario: str = "developer_morning"  # developer_morning, research_assistant, coding_assistant


@router.get("/status", response_class=JSONResponse)
async def get_release_status():
    """Returns v1.0 Release Candidate status and subsystem audit."""
    svc = get_release_service()
    return svc.get_v1_release_status()


@router.post("/onboarding", response_class=JSONResponse)
async def complete_onboarding(req: OnboardingRequest):
    """Completes user onboarding setup."""
    svc = get_release_service()
    return svc.onboarding.complete_onboarding(req.username, req.primary_provider, req.theme)


@router.post("/demo/run", response_class=JSONResponse)
async def run_live_demo(req: DemoRunRequest):
    """Executes live E2E demonstration workflow."""
    svc = get_release_service()
    return svc.run_live_demo(req.scenario)


@router.get("/marketplace", response_class=JSONResponse)
async def list_marketplace_plugins():
    """Returns plugin marketplace discovery catalog."""
    svc = get_release_service()
    return {"plugins": svc.marketplace.list_marketplace_plugins()}


@router.post("/portfolio/export", response_class=JSONResponse)
async def export_portfolio():
    """Exports portfolio presentation assets & architecture summary."""
    svc = get_release_service()
    return svc.export_portfolio_package()
