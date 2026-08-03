"""
Browser Agent for Project Astra.
Specialist agent for Playwright web automation, tab management, and page content extraction.
"""

import time
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class BrowserAgent(BaseAgent):
    """
    Specialist agent responsible for browser tab automation, DOM navigation, and page reading.
    """

    def __init__(self):
        super().__init__(
            name="BrowserAgent",
            description="Specialist agent for Playwright web browser interaction and page reading."
        )

    def can_handle(self, task: AgentTask) -> bool:
        desc = task.description.lower()
        return task.target_agent_type == "BrowserAgent" or any(kw in desc for kw in ["browser", "page", "tab", "url", "youtube"])

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        start_time = time.time()
        desc = task.description.lower()

        try:
            if "youtube" in desc:
                query = task.input_data.get("query", "LangGraph tutorials")
                data = self._invoke_tool("browser.youtube_search", {"query": query})
            elif "read" in desc or "summarize" in desc or "extract" in desc:
                data = self._invoke_tool("browser.read_page", {})
            else:
                url = task.input_data.get("url", "https://google.com")
                data = self._invoke_tool("browser.open_url", {"url": url})

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
            logger.error(f"[{self.name}] Browser task failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                success=False,
                error_message=str(e),
                execution_time_ms=elapsed
            )
