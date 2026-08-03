"""
Agent Registry Module for Project Astra.
Central registry for discovering, registering, and listing specialist agent instances.
"""

from typing import Dict, List, Optional, Any
from app.utils.logger import logger


class AgentRegistry:
    """
    Central discovery registry for Astra specialist agents.
    """

    def __init__(self):
        self._agents: Dict[str, Any] = {}

    def register(self, agent: Any) -> None:
        """
        Registers an agent instance by name.
        """
        name = getattr(agent, "name", agent.__class__.__name__)
        if name in self._agents:
            logger.warning(f"[AgentRegistry] Overwriting existing agent registration for '{name}'.")
        self._agents[name] = agent
        logger.info(f"[AgentRegistry] Registered specialist agent: '{name}'")

    def get_agent(self, name: str) -> Optional[Any]:
        """Retrieves a registered agent instance by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """Returns a list of all registered agent names."""
        return list(self._agents.keys())

    def get_all_agents(self) -> List[Any]:
        """Returns all registered agent instances."""
        return list(self._agents.values())


# Global default AgentRegistry singleton
agent_registry = AgentRegistry()
