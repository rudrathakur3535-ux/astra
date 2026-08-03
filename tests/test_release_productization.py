"""
Comprehensive Final Unit & Integration Test Suite for Astra OS v1.0 Release Candidate & Productization.
"""

import pytest
import time
import os
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.release.onboarding_manager import OnboardingManager
from app.release.marketplace_service import MarketplaceService
from app.release.productization_engine import ProductizationEngine
from demo.demo_workflows import DemoWorkflowRunner

from scripts.build import build_astra_os
from scripts.release import create_release_package
from scripts.generate_docs import generate_documentation

from app.services.release_service import ReleaseService
from app.api.release_api import router as release_router


class TestOnboardingAndMarketplace:
    """Tests User Onboarding Manager and Plugin Marketplace Service."""

    def test_onboarding_manager(self):
        mgr = OnboardingManager()
        assert mgr.is_onboarded() is False

        res = mgr.complete_onboarding(username="rudra", primary_provider="gemini")
        assert res["status"] == "onboarding_completed"
        assert mgr.is_onboarded() is True

    def test_marketplace_service(self):
        m_svc = MarketplaceService()
        plugins = m_svc.list_marketplace_plugins()
        assert len(plugins) >= 2

        inst_res = m_svc.install_plugin("spotify_focus_mode")
        assert inst_res["status"] == "installed"

        tog_res = m_svc.toggle_plugin_status("spotify_focus_mode", enabled=True)
        assert tog_res["enabled"] is True


class TestProductizationAndDemos:
    """Tests Productization Engine, Portfolio export, and E2E Demo Workflows."""

    def test_productization_engine_audit(self):
        engine = ProductizationEngine()
        audit = engine.audit_release_readiness()
        assert audit["overall_status"] == "PRODUCTION_READY"
        assert audit["subsystems_count"] == 19

        portfolio = engine.export_portfolio_assets()
        assert portfolio["version"] == "v1.0.0-RC"
        assert len(portfolio["architecture_highlights"]) >= 3

    def test_e2e_demo_workflows(self):
        runner = DemoWorkflowRunner()

        # Demo 1: Morning Routine
        d1 = runner.run_developer_morning_routine()
        assert d1["status"] == "COMPLETED"
        assert len(d1["steps_executed"]) == 5

        # Demo 2: Research Assistant
        d2 = runner.run_research_assistant_workflow("LangGraph")
        assert d2["status"] == "COMPLETED"

        # Demo 3: Coding Assistant
        d3 = runner.run_coding_assistant_workflow("astra-os")
        assert d3["status"] == "COMPLETED"


class TestAutomationScripts:
    """Tests build, release, and documentation generation scripts."""

    def test_build_script(self):
        res = build_astra_os()
        assert res["status"] == "SUCCESS"
        assert res["app_verified"] is True

    def test_release_script(self):
        pkg = create_release_package("v1.0.0-RC")
        assert pkg["status"] == "packaged"
        assert "Astra OS v1.0.0 Release Candidate" in pkg["changelog"]

    def test_generate_docs_script(self):
        docs = generate_documentation()
        assert docs["title"] == "Astra OS v1.0 Production Documentation"
        assert len(docs["sections"]) >= 5


class TestMasterReleaseServiceAndAPI:
    """Tests Master Release Service and FastAPI v1.0 Release Router."""

    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(release_router)
        self.client = TestClient(self.app)

    def test_release_status_endpoint(self):
        res = self.client.get("/api/v1/release/status")
        assert res.status_code == 200
        assert res.json()["overall_status"] == "PRODUCTION_READY"

    def test_onboarding_endpoint(self):
        res = self.client.post("/api/v1/release/onboarding", json={
            "username": "rudra",
            "primary_provider": "gemini"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "onboarding_completed"

    def test_demo_run_endpoint(self):
        res = self.client.post("/api/v1/release/demo/run", json={"scenario": "developer_morning"})
        assert res.status_code == 200
        assert res.json()["status"] == "COMPLETED"

    def test_marketplace_endpoint(self):
        res = self.client.get("/api/v1/release/marketplace")
        assert res.status_code == 200
        assert len(res.json()["plugins"]) >= 2

    def test_portfolio_export_endpoint(self):
        res = self.client.post("/api/v1/release/portfolio/export")
        assert res.status_code == 200
        assert "project_name" in res.json()
