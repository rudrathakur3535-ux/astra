"""
Agent Selector Module for Project Astra.
Matches tasks to specialist agents using capability scoring and can_handle() evaluation.
"""

from typing import Optional, List, Any
from app.models.agent_task import AgentTask
from app.orchestrator.agent_registry import AgentRegistry, agent_registry
from app.utils.logger import logger


class AgentSelector:
    """
    Intelligent selector mapping tasks to appropriate specialist agents.
    """

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or agent_registry

    def select_agent_for_task(self, task: AgentTask) -> Optional[Any]:
        """
        Selects the single best specialist agent for a given task.
        """
        # 1. Direct match by target_agent_type if specified
        if task.target_agent_type:
            agent = self.registry.get_agent(task.target_agent_type)
            if agent and getattr(agent, "can_handle", lambda t: True)(task):
                logger.debug(f"[AgentSelector] Selected agent '{agent.name}' by direct target type.")
                return agent

        # 2. Dynamic discovery via can_handle() evaluation across all registered agents
        for agent in self.registry.get_all_agents():
            can_handle_func = getattr(agent, "can_handle", None)
            if callable(can_handle_func) and can_handle_func(task):
                logger.info(f"[AgentSelector] Selected specialist agent '{agent.name}' for task '{task.task_id[:8]}'")
                return agent

        logger.warning(f"[AgentSelector] No specialist agent found capable of handling task: '{task.description}'")
        return None

# Global default AgentSelector singleton
agent_selector = AgentSelector()
