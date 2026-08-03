"""
Diagnostic Report Bundler for Project Astra OS.
Bundles logs, traces, health status, metrics, and hardware specs into exportable diagnostic archives.
"""

from typing import Dict, Any, Optional
import platform
import psutil
from app.models.diagnostic_report import DiagnosticReport
from app.observability.dashboard_service import DashboardService


class DiagnosticBundler:
    """
    Bundles diagnostic data for user support and system troubleshooting.
    """

    def __init__(self, dashboard_service: Optional[DashboardService] = None):
        self.dashboard_service = dashboard_service or DashboardService()

    def get_system_specs(self) -> Dict[str, Any]:
        """Collects hardware and OS environment details."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
            "cpu_usage_percent": psutil.cpu_percent(interval=None)
        }

    def generate_diagnostic_report(self, app_version: str = "1.0.0") -> DiagnosticReport:
        """
        Generates a complete DiagnosticReport model containing system state and logs.
        """
        summary = self.dashboard_service.get_dashboard_summary()
        sys_info = summary.get("system", {})
        health_subsystems = sys_info.get("subsystems", {})
        logs = summary.get("logs", [])
        active_traces = list(summary.get("traces", {}).keys())

        report = DiagnosticReport(
            app_version=app_version,
            platform=f"{platform.system()} {platform.release()}",
            overall_health=sys_info.get("status", "healthy"),
            error_count=summary.get("summary_cards", {}).get("error_count", 0),
            active_trace_ids=active_traces,
            subsystems_health=health_subsystems,
            recent_logs=logs,
            system_specs=self.get_system_specs()
        )
        return report
