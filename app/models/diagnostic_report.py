"""
Diagnostic Report Model for Project Astra OS.
Represents system diagnostics payloads for troubleshooting and crash reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time
import uuid


@dataclass
class DiagnosticReport:
    """
    Diagnostic report payload containing system state, logs, and subsystem health reports.
    """
    app_version: str
    platform: str
    overall_health: str
    error_count: int
    active_trace_ids: List[str] = field(default_factory=list)
    subsystems_health: Dict[str, Any] = field(default_factory=dict)
    recent_logs: List[Dict[str, Any]] = field(default_factory=list)
    system_specs: Dict[str, Any] = field(default_factory=dict)
    report_id: str = field(default_factory=lambda: f"diag-{uuid.uuid4().hex[:8]}")
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "created_at": self.created_at,
            "app_version": self.app_version,
            "platform": self.platform,
            "overall_health": self.overall_health,
            "error_count": self.error_count,
            "active_trace_ids": self.active_trace_ids,
            "subsystems_health": self.subsystems_health,
            "recent_logs": self.recent_logs,
            "system_specs": self.system_specs
        }
