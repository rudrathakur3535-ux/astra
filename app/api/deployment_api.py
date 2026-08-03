"""
FastAPI Deployment & Distribution API Router for Project Astra OS.
Provides endpoints for version status, first-time setup wizard, auto-updater, diagnostics, and crash reports.
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json

from app.deployment.setup_wizard import SetupWizard
from app.deployment.auto_updater import AutoUpdater
from app.deployment.diagnostic_bundler import DiagnosticBundler
from app.deployment.crash_reporter import CrashReporter
from app.models.deployment_manifest import DeploymentManifest, ReleaseChannel, TargetPlatform

router = APIRouter(prefix="/api/deployment", tags=["deployment"])

# Global Singleton Instances
_setup_wizard_instance: Optional[SetupWizard] = None
_auto_updater_instance: Optional[AutoUpdater] = None
_diagnostic_bundler_instance: Optional[DiagnosticBundler] = None
_crash_reporter_instance: Optional[CrashReporter] = None


def get_setup_wizard() -> SetupWizard:
    global _setup_wizard_instance
    if _setup_wizard_instance is None:
        _setup_wizard_instance = SetupWizard()
    return _setup_wizard_instance


def get_auto_updater() -> AutoUpdater:
    global _auto_updater_instance
    if _auto_updater_instance is None:
        _auto_updater_instance = AutoUpdater()
    return _auto_updater_instance


def get_diagnostic_bundler() -> DiagnosticBundler:
    global _diagnostic_bundler_instance
    if _diagnostic_bundler_instance is None:
        _diagnostic_bundler_instance = DiagnosticBundler()
    return _diagnostic_bundler_instance


def get_crash_reporter() -> CrashReporter:
    global _crash_reporter_instance
    if _crash_reporter_instance is None:
        _crash_reporter_instance = CrashReporter()
    return _crash_reporter_instance


class SetupRequest(BaseModel):
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    voice_engine: str = "elevenlabs"
    wake_word: str = "Hey Astra"


class CrashReportRequest(BaseModel):
    exception_message: str
    subsystem: str = "runtime"
    trace_id: Optional[str] = None
    stack_trace: Optional[str] = None


@router.get("/status", response_class=JSONResponse)
async def get_deployment_status():
    """
    Returns app version, build number, platform, and setup status.
    """
    updater = get_auto_updater()
    wizard = get_setup_wizard()
    return {
        "version": updater.current_version,
        "build_number": updater.current_build,
        "setup_completed": wizard.is_setup_completed(),
        "status": "online"
    }


@router.post("/setup", response_class=JSONResponse)
async def execute_setup_wizard(req: SetupRequest):
    """
    Executes first-time setup onboarding wizard configuration.
    """
    wizard = get_setup_wizard()
    res = wizard.run_setup(
        llm_provider=req.llm_provider,
        openai_api_key=req.openai_api_key,
        gemini_api_key=req.gemini_api_key,
        elevenlabs_api_key=req.elevenlabs_api_key,
        voice_engine=req.voice_engine,
        wake_word=req.wake_word
    )
    return res


@router.get("/update", response_class=JSONResponse)
async def check_update():
    """
    Checks if a software update is available.
    """
    updater = get_auto_updater()
    # Mock latest release manifest comparison
    latest = DeploymentManifest(version="1.0.0", build_number=100, release_notes="Astra OS Stable")
    return updater.check_for_updates(latest)


@router.post("/update/apply", response_class=JSONResponse)
async def apply_update(latest_version: str = Body("1.0.1", embed=True)):
    """
    Applies software update.
    """
    updater = get_auto_updater()
    manifest = DeploymentManifest(version=latest_version, build_number=101, release_notes="Bug fixes & performance optimizations.")
    return updater.apply_update(manifest)


@router.get("/diagnostics", response_class=JSONResponse)
async def get_diagnostics():
    """
    Generates and downloads a diagnostic report archive payload.
    """
    bundler = get_diagnostic_bundler()
    report = bundler.generate_diagnostic_report()
    return report.to_dict()


@router.post("/crash-report", response_class=JSONResponse)
async def submit_crash_report(req: CrashReportRequest):
    """
    Submits a runtime crash report for diagnostics and troubleshooting.
    """
    reporter = get_crash_reporter()
    exc = Exception(req.exception_message)
    crash = reporter.record_crash(
        exception=exc,
        subsystem=req.subsystem,
        trace_id=req.trace_id,
        context_metadata={"stack_trace": req.stack_trace}
    )
    return {"status": "recorded", "crash_id": crash["crash_id"]}
