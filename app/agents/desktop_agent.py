"""
Desktop Agent for Project Astra.
Specialist agent for OS application launching, window focus, system metrics, and clipboard operations.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class DesktopAgent(BaseAgent):
    """
    Specialist agent managing desktop OS hands (window management, app launching, system metrics).
    """

    def __init__(self):
        super().__init__(
            name="DesktopAgent",
            description="Specialist agent for desktop application management, windows, clipboard, and RAM metrics."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "DesktopAgent" or any(kw in desc for kw in ["desktop", "app", "window", "launch", "ram", "system", "clipboard"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        desc = task.description.lower()

        try:
            if "launch" in desc or "vscode" in desc or "app" in desc:
                app_name = task.input_data.get("app_name", "calc")
                data = self._invoke_tool("launch_app", {"app_name": app_name})
            elif "window" in desc:
                data = self._invoke_tool("list_windows", {})
            else:
                data = self._invoke_tool("get_system_info", {})

            elapsed = (time.time() - start_time) * 1000.0
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=True,
                data=data,
                execution_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"[{self.name}] Desktop task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
