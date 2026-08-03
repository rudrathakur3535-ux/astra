"""
Provider Health Monitor for Project Astra OS.
Continuously monitors AI provider latencies, health states, and failover status.
"""

from typing import Dict, Any, List, Optional
from app.providers.provider_router import ProviderRouter
from app.models.provider_status import ProviderStatus, ProviderState


class ProviderHealthMonitor:
    """
    Monitors provider health and latency metrics.
    """

    def __init__(self, provider_router: Optional[ProviderRouter] = None):
        self.router = provider_router or ProviderRouter()

    def check_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Runs health check across all registered AI providers.
        """
        statuses = {}
        for name in self.router.list_providers():
            provider = self.router.get_provider(name)
            if provider:
                try:
                    status = provider.get_status()
                    statuses[name] = status.to_dict()
                except Exception:
                    statuses[name] = ProviderStatus(
                        provider_name=name,
                        state=ProviderState.OFFLINE,
                        latency_ms=0.0
                    ).to_dict()

        return statuses

    def get_healthy_providers(self) -> List[str]:
        """Returns names of all currently healthy providers."""
        all_status = self.check_all_providers()
        return [
            name for name, info in all_status.items()
            if info.get("state") in (ProviderState.HEALTHY.value, "healthy")
        ]
