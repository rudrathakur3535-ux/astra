"""
Master Release & Productization Service for Project Astra OS v1.0.
Orchestrates onboarding, live E2E demo workflows, plugin marketplace, and portfolio exports.
"""

from typing import Dict, List, Any, Optional
from app.release.onboarding_manager import OnboardingManager
from app.release.marketplace_service import MarketplaceService
from app.release.productization_engine import ProductizationEngine
from demo.demo_workflows import DemoWorkflowRunner


class ReleaseService:
    """
    Master Release Platform Orchestrator.
    """

    def __init__(self):
        self.onboarding = OnboardingManager()
        self.marketplace = MarketplaceService()
        self.productization = ProductizationEngine()
        self.demo_runner = DemoWorkflowRunner()

    def get_v1_release_status(self) -> Dict[str, Any]:
        """Returns complete v1.0 release readiness audit status."""
        return self.productization.audit_release_readiness()

    def run_live_demo(self, scenario: str = "developer_morning") -> Dict[str, Any]:
        """
        Executes interactive E2E live demonstration scenarios.
        Options: 'developer_morning', 'research_assistant', 'coding_assistant'.
        """
        if scenario == "research_assistant":
            return self.demo_runner.run_research_assistant_workflow()
        elif scenario == "coding_assistant":
            return self.demo_runner.run_coding_assistant_workflow()
        else:
            return self.demo_runner.run_developer_morning_routine()

    def export_portfolio_package(self) -> Dict[str, Any]:
        """Exports portfolio metrics, architecture highlights, and asset summary."""
        return self.productization.export_portfolio_assets()
