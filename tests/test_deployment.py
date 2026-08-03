"""
Comprehensive Unit Test Suite for Deployment, Packaging & Distribution Platform.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.models.deployment_manifest import DeploymentManifest, ReleaseChannel, TargetPlatform
from app.models.diagnostic_report import DiagnosticReport
from app.deployment.setup_wizard import SetupWizard
from app.deployment.auto_updater import AutoUpdater
from app.deployment.diagnostic_bundler import DiagnosticBundler
from app.deployment.crash_reporter import CrashReporter
from app.deployment.packager_service import PackagerService
from app.api.deployment_api import router as deployment_router


class TestSetupWizard:
    """Tests first-time onboarding setup wizard."""

    def test_setup_wizard_execution(self, tmp_path):
        wizard = SetupWizard()
        res = wizard.run_setup(
            llm_provider="openai",
            openai_api_key="sk-test-key-12345",
            voice_engine="elevenlabs",
            wake_word="Hey Astra"
        )

        assert res["status"] == "success"
        assert res["setup_completed"] is True
        assert "OPENAI_API_KEY" in res["secrets_configured"]
        assert wizard.is_setup_completed() is True


class TestAutoUpdater:
    """Tests version checking, manifest comparison, and hot-patch updates."""

    def test_version_parsing_and_update_check(self):
        updater = AutoUpdater(current_version="1.0.0", current_build=100)
        latest = DeploymentManifest(version="1.0.1", build_number=101, release_notes="Fixes")

        check_res = updater.check_for_updates(latest)
        assert check_res["update_available"] is True
        assert check_res["latest_version"] == "1.0.1"

    def test_apply_update(self):
        updater = AutoUpdater(current_version="1.0.0", current_build=100)
        latest = DeploymentManifest(version="1.1.0", build_number=110)

        update_res = updater.apply_update(latest)
        assert update_res["status"] == "updated"
        assert updater.current_version == "1.1.0"


class TestDiagnosticBundlerAndCrashReporter:
    """Tests diagnostic report generation and crash exception recording."""

    def test_diagnostic_report_generation(self):
        bundler = DiagnosticBundler()
        report = bundler.generate_diagnostic_report(app_version="1.0.0")

        assert report.app_version == "1.0.0"
        assert report.report_id.startswith("diag-")
        assert "cpu_count" in report.system_specs
        assert "ram_total_gb" in report.system_specs

    def test_crash_reporter_stack_trace_capture(self):
        reporter = CrashReporter()
        try:
            raise ValueError("Test crash exception")
        except Exception as e:
            crash = reporter.record_crash(e, subsystem="test_subsystem", trace_id="trace-999")

        assert crash["crash_id"].startswith("crash-")
        assert crash["exception_type"] == "ValueError"
        assert crash["trace_id"] == "trace-999"
        assert "ValueError: Test crash exception" in crash["stack_trace"]
        assert reporter.get_crash_count() == 1


class TestPackagerService:
    """Tests installer package build spec generation."""

    def test_packager_spec_generation(self):
        packager = PackagerService()
        win_spec = packager.generate_installer_spec(TargetPlatform.WINDOWS)
        mac_spec = packager.generate_installer_spec(TargetPlatform.MACOS)

        assert win_spec["target_platform"] == "windows"
        assert win_spec["installer_config"]["installer_type"] == "NSIS (.exe) / MSI"
        assert mac_spec["target_platform"] == "macos"
        assert mac_spec["installer_config"]["installer_type"] == "DMG"


class TestDeploymentAPIEndpoints:
    """Tests FastAPI Deployment Router REST endpoints."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(deployment_router)
        self.client = TestClient(self.app)

    def test_deployment_status_endpoint(self):
        res = self.client.get("/api/deployment/status")
        assert res.status_code == 200
        data = res.json()
        assert "version" in data
        assert "status" in data

    def test_setup_wizard_endpoint(self):
        res = self.client.post("/api/deployment/setup", json={
            "llm_provider": "gemini",
            "gemini_api_key": "AIzaSyTestKey",
            "voice_engine": "pyttsx3"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "success"

    def test_update_check_and_apply_endpoint(self):
        res = self.client.get("/api/deployment/update")
        assert res.status_code == 200

        apply_res = self.client.post("/api/deployment/update/apply", json={"latest_version": "1.0.5"})
        assert apply_res.status_code == 200
        assert apply_res.json()["status"] == "updated"

    def test_diagnostics_endpoint(self):
        res = self.client.get("/api/deployment/diagnostics")
        assert res.status_code == 200
        assert "system_specs" in res.json()

    def test_crash_report_endpoint(self):
        res = self.client.post("/api/deployment/crash-report", json={
            "exception_message": "Unhandled zero division",
            "subsystem": "calculator",
            "trace_id": "trace-555"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "recorded"
