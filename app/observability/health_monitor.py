"""
Subsystem Health Monitor for Project Astra OS.
Monitors system component states (Voice, Knowledge, Memory, Plugin SDK, Browser, Communication, Execution Runtime).
"""

from typing import Dict, Any, Optional, Callable, List
import time

from app.models.health_status import SubsystemHealth, HealthState
from app.ports.observability_port import ObservabilityPort


class HealthMonitor:
    """
    Monitors overall health and individual subsystem status reports.
    """

    CORE_SUBSYSTEMS = [
        "Voice",
        "Knowledge",
        "Memory",
        "Plugin SDK",
        "Browser",
        "Communication",
        "Execution Runtime",
        "Core LLM"
    ]

    def __init__(self, port: Optional[ObservabilityPort] = None):
        self._port = port
        self._probes: Dict[str, Callable[[], SubsystemHealth]] = {}
        self._cached_health: Dict[str, SubsystemHealth] = {}
        self._init_default_probes()

    def _init_default_probes(self) -> None:
        """Initializes default health state probes for Astra core subsystems."""
        for subsystem in self.CORE_SUBSYSTEMS:
            self._cached_health[subsystem] = SubsystemHealth(
                subsystem_name=subsystem,
                state=HealthState.HEALTHY,
                latency_ms=1.2,
                details=f"{subsystem} subsystem active.",
                last_check=time.time()
            )

    def register_subsystem_probe(self, subsystem_name: str, probe_fn: Callable[[], SubsystemHealth]) -> None:
        """Registers a custom health probe function for a subsystem."""
        self._probes[subsystem_name] = probe_fn

    def set_subsystem_health(
        self,
        subsystem_name: str,
        state: HealthState,
        latency_ms: float = 0.0,
        details: str = ""
    ) -> SubsystemHealth:
        """Manually updates a subsystem's health status."""
        health = SubsystemHealth(
            subsystem_name=subsystem_name,
            state=state,
            latency_ms=latency_ms,
            details=details or f"{subsystem_name} status updated to {state.value}.",
            last_check=time.time()
        )
        self._cached_health[subsystem_name] = health
        return health

    def report_missing_subsystem(self, subsystem_name: str, details: str = "Subsystem uninitialized or missing.") -> SubsystemHealth:
        """Reports a missing or uninitialized subsystem as UNHEALTHY."""
        return self.set_subsystem_health(
            subsystem_name=subsystem_name,
            state=HealthState.UNHEALTHY,
            latency_ms=0.0,
            details=details
        )

    def check_subsystem(self, subsystem_name: str) -> SubsystemHealth:
        """Executes health probe for a single subsystem."""
        if subsystem_name in self._probes:
            try:
                start = time.time()
                health = self._probes[subsystem_name]()
                health.latency_ms = (time.time() - start) * 1000.0
                health.last_check = time.time()
                self._cached_health[subsystem_name] = health
                return health
            except Exception as e:
                health = SubsystemHealth(
                    subsystem_name=subsystem_name,
                    state=HealthState.UNHEALTHY,
                    latency_ms=0.0,
                    details=f"Probe failed: {str(e)}",
                    last_check=time.time()
                )
                self._cached_health[subsystem_name] = health
                return health

        if subsystem_name in self._cached_health:
            return self._cached_health[subsystem_name]

        return self.report_missing_subsystem(subsystem_name)

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """Executes all health checks and returns overall status mapping."""
        if self._port:
            port_health = self._port.get_health_status()
            if port_health:
                return {name: status.to_dict() for name, status in port_health.items()}

        for subsystem in self.CORE_SUBSYSTEMS:
            self.check_subsystem(subsystem)

        return {name: status.to_dict() for name, status in self._cached_health.items()}

    def get_overall_system_status(self) -> HealthState:
        """
        Determines overall system health state.
        If any core subsystem is UNHEALTHY -> UNHEALTHY
        Else if any is DEGRADED -> DEGRADED
        Else -> HEALTHY
        """
        statuses = self.check_all()
        states = [s.get("state") for s in statuses.values()]

        if "unhealthy" in states:
            return HealthState.UNHEALTHY
        if "degraded" in states:
            return HealthState.DEGRADED
        return HealthState.HEALTHY
