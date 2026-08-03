"""
Research Agent for Project Astra.
Specialist agent for web search, information synthesis, and research event dispatches.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class ResearchAgent(BaseAgent):
    """
    Specialist agent responsible for web research and information gathering.
    """

    def __init__(self):
        super().__init__(
            name="ResearchAgent",
            description="Specialist agent for web search and research information synthesis."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "ResearchAgent" or any(kw in desc for kw in ["research", "google", "search"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        query = task.input_data.get("query", task.description)

        try:
            # Route execution through ToolRouter
            data = self._invoke_tool("browser.google_search", {"query": query})
            
            # Event-Driven Architecture (Stretch Goal ⭐): Publish event to EventBus
            if context.event_bus:
                context.event_bus.publish("RESEARCH_COMPLETED", {"query": query, "result": data})

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
            logger.error(f"[{self.name}] Research task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
