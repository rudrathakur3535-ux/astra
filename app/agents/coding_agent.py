"""
Coding Agent for Project Astra.
Specialist agent for folder creation, file management, code synthesis, and project scaffolding.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class CodingAgent(BaseAgent):
    """
    Specialist agent responsible for code generation, folder creation, and workspace file editing.
    """

    def __init__(self):
        super().__init__(
            name="CodingAgent",
            description="Specialist agent for coding tasks, directory creation, and file synthesis."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "CodingAgent" or any(kw in desc for kw in ["code", "folder", "directory", "project", "file"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        folder_name = task.input_data.get("folder_name", "FinanceAI")

        try:
            data = self._invoke_tool("create_folder", {"folder_name": folder_name})
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
            logger.error(f"[{self.name}] Coding task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
