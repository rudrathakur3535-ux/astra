"""
Communication Agent for Project Astra.
Specialist agent for user notifications, email alerts, and messaging dispatches.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class CommunicationAgent(BaseAgent):
    """
    Specialist agent managing communications, notifications, and user output dispatches.
    """

    def __init__(self):
        super().__init__(
            name="CommunicationAgent",
            description="Specialist agent for messaging, notifications, and communication dispatching."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "CommunicationAgent" or any(kw in desc for kw in ["notify", "email", "message", "whatsapp", "speak"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        message = task.input_data.get("message", task.description)

        try:
            logger.info(f"[{self.name}] Dispatching notification: '{message}'")
            elapsed = (time.time() - start_time) * 1000.0
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=True,
                data={"dispatched_message": message, "status": "sent"},
                execution_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"[{self.name}] Communication task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
