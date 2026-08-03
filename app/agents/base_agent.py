"""
Base Agent Abstract Class for Project Astra.
Enforces common interface contract across all specialist and manager agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time

from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.tools.tool_router import tool_router, ToolRouter
from app.utils.logger import logger


class BaseAgent(ABC):
    """
    Abstract Base Class for all Astra Specialist Agents.
    """

    def __init__(self, name: str, description: str, router: Optional[ToolRouter] = None):
        self.name = name
        self.description = description
        self.router = router or tool_router

    @abstractmethod
    def can_handle(self, task: AgentTask) -> bool:
        """Returns True if this agent is capable of handling the specified task."""
        pass

    @abstractmethod
    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """Executes the assigned task using shared context and tool router."""
        pass

    def _invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Helper to invoke tools through Astra's central ToolRouter & PermissionLayer."""
        logger.info(f"[{self.name}] Invoking tool '{tool_name}' with args: {arguments}")
        response = self.router.execute({"tool_name": tool_name, "arguments": arguments})
        if not response.success:
            raise RuntimeError(f"Tool '{tool_name}' failed: {response.error_message}")
        return response.data
