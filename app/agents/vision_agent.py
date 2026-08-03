"""
Vision Agent for Project Astra.
Specialist agent for desktop screen capture, grid overlays, ROI inspection, and visual UI element searching.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class VisionAgent(BaseAgent):
    """
    Specialist agent responsible for screen perception and multimodal vision analysis.
    """

    def __init__(self):
        super().__init__(
            name="VisionAgent",
            description="Specialist agent for screen capture, visual perception, and grid annotations."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "VisionAgent" or any(kw in desc for kw in ["screen", "vision", "screenshot", "grid", "capture", "roi"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        desc = task.description.lower()

        try:
            if "analyze" in desc:
                data = self._invoke_tool("vision.analyze_screen", {"max_dimension": 1024})
            elif "grid" in desc:
                data = self._invoke_tool("vision.capture_screen", {"grid_overlay": True})
            else:
                data = self._invoke_tool("vision.capture_screen", {"grid_overlay": False})

            if data and isinstance(data, dict) and "filepath" in data:
                context.add_artifact(data["filepath"])

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
            logger.error(f"[{self.name}] Vision task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
