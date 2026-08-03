"""
Manager Agent for Project Astra.
Master delegator breaking user goals into multi-agent workflow DAG graphs.
"""

from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.agent_task import AgentTask, TaskPriority
from app.models.agent_result import AgentResult
from app.models.workflow import Workflow, WorkflowMode
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class ManagerAgent(BaseAgent):
    """
    Manager Agent responsible for analyzing high-level goals and delegating sub-tasks to specialist agents.
    """

    def __init__(self):
        super().__init__(
            name="ManagerAgent",
            description="Master manager that breaks goals into multi-agent workflow DAG graphs."
        )

    def can_handle(self, task: AgentTask) -> bool:
        return task.target_agent_type in ("manager", "general", "workflow")

    def execute(self, task: AgentTask, context: AgentContext) -> AgentResult:
        workflow = self.create_workflow_for_goal(task.description)
        return AgentResult(
            task_id=task.task_id,
            agent_name=self.name,
            success=True,
            data={"workflow_id": workflow.workflow_id, "tasks_count": len(workflow.tasks)}
        )

    def create_workflow_for_goal(self, goal_text: str) -> Workflow:
        """
        Decomposes natural language goal into specialized AgentTask nodes with DAG dependencies.
        """
        logger.info(f"[ManagerAgent] Decomposing goal into specialist agent workflow: '{goal_text}'")
        text = goal_text.lower()
        tasks: List[AgentTask] = []

        # Complex Goal Example: "Research LangGraph, summarize it, save the notes, and open VS Code."
        if "research" in text and ("save" in text or "vscode" in text or "code" in text):
            t1 = AgentTask(
                description="Search for LangGraph tutorials and documentation",
                target_agent_type="ResearchAgent",
                input_data={"query": "LangGraph tutorials"}
            )
            t2 = AgentTask(
                description="Extract and summarize page content",
                target_agent_type="BrowserAgent",
                dependencies=[t1.task_id]
            )
            t3 = AgentTask(
                description="Store summary notes into long-term memory",
                target_agent_type="MemoryAgent",
                input_data={"fact": "LangGraph is an agentic workflow orchestration framework."},
                dependencies=[t2.task_id]
            )
            t4 = AgentTask(
                description="Open VS Code or workspace editor",
                target_agent_type="DesktopAgent",
                input_data={"app_name": "vscode"},
                dependencies=[t3.task_id]
            )
            tasks.extend([t1, t2, t3, t4])

        # Project Creation Goal Example: "Create a project called FinanceAI"
        elif "create" in text and ("project" in text or "financeai" in text):
            t1 = AgentTask(
                description="Create project directory for FinanceAI",
                target_agent_type="CodingAgent",
                input_data={"folder_name": "FinanceAI"}
            )
            t2 = AgentTask(
                description="Inspect system resource allocation",
                target_agent_type="DesktopAgent",
                input_data={}
            )
            tasks.extend([t1, t2])

        # Default Multi-Agent Workflow
        else:
            t1 = AgentTask(
                description=f"Perform general task: {goal_text}",
                target_agent_type="DesktopAgent"
            )
            tasks.append(t1)

        workflow = Workflow(
            name=f"Workflow_{goal_text[:20]}",
            goal_description=goal_text,
            tasks=tasks,
            mode=WorkflowMode.HYBRID
        )
        logger.info(f"[ManagerAgent] Created Workflow with {len(tasks)} specialist agent tasks.")
        return workflow
