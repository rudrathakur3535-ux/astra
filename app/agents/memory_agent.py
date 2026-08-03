"""
Memory Agent for Project Astra.
Specialist agent for long-term fact storage, semantic memory retrieval, and memory reflection.
"""

import time
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.memory.memory_service import MemoryService
from app.models.memory_record import MemoryCategory
from app.utils.logger import logger


class MemoryAgent(BaseAgent):
    """
    Specialist agent managing long-term semantic knowledge, user facts, and memory reflection.
    """

    def __init__(self, memory_service: Optional[MemoryService] = None):
        super().__init__(
            name="MemoryAgent",
            description="Specialist agent for storing, retrieving, and reflecting on long-term memory facts."
        )
        self.memory_service = memory_service

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "MemoryAgent" or any(kw in desc for kw in ["memory", "fact", "remember", "store", "recall", "reflect"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        fact_text = task.input_data.get("fact") or task.description

        try:
            if not self.memory_service:
                self.memory_service = MemoryService()

            rec = self.memory_service.remember_fact(
                fact=fact_text,
                category=MemoryCategory.PROJECTS,
                importance=8
            )

            elapsed = (time.time() - start_time) * 1000.0
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=True,
                data={"record_id": rec.record_id, "fact": rec.content},
                execution_time_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000.0
            logger.error(f"[{self.name}] Memory task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
