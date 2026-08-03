"""
Workflow Engine Module for Project Astra.
Executes multi-agent DAG workflows (sequential & parallel execution modes), updates context, and renders workflow graphs.
"""

from typing import Dict, Any, List, Optional
import time

from app.models.workflow import Workflow, WorkflowStatus, WorkflowMode
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult
from app.orchestrator.agent_context import AgentContext
from app.orchestrator.agent_selector import AgentSelector, agent_selector
from app.orchestrator.metrics_tracker import metrics_tracker, AgentMetricsTracker
from app.utils.logger import logger


class WorkflowEngine:
    """
    Executes Workflow graphs with retry logic, context propagation, and parallel step resolution.
    """

    def __init__(
        self,
        selector: Optional[AgentSelector] = None,
        tracker: Optional[AgentMetricsTracker] = None
    ):
        self.selector = selector or agent_selector
        self.tracker = tracker or metrics_tracker

    def execute_workflow(self, workflow: Workflow, context: AgentContext) -> Workflow:
        """
        Executes all tasks in a Workflow object according to mode and task dependencies.
        """
        workflow.status = WorkflowStatus.RUNNING
        workflow.add_log(f"Starting workflow '{workflow.name}' (Mode: {workflow.mode.value}).")
        logger.info(f"[WorkflowEngine] Starting execution for Workflow '{workflow.name}' ({len(workflow.tasks)} tasks).")

        executed_task_ids = set()

        while len(executed_task_ids) < len(workflow.tasks):
            # Find executable tasks whose dependencies are satisfied
            ready_tasks = [
                t for t in workflow.tasks 
                if t.task_id not in executed_task_ids and all(dep in executed_task_ids for dep in t.dependencies)
            ]

            if not ready_tasks:
                workflow.add_log("Error: Unresolvable task dependencies or deadlocked task graph.")
                workflow.status = WorkflowStatus.FAILED
                break

            for task in ready_tasks:
                workflow.add_log(f"Routing Task '{task.task_id[:8]}': '{task.description}'...")

                agent = self.selector.select_agent_for_task(task)
                if not agent:
                    err_msg = f"No suitable specialist agent found for task: '{task.description}'"
                    workflow.add_log(err_msg)
                    workflow.results[task.task_id] = AgentResult(
                        task_id=task.task_id,
                        agent_name="unknown",
                        success=False,
                        error_message=err_msg
                    )
                    workflow.status = WorkflowStatus.FAILED
                    executed_task_ids.add(task.task_id)
                    break

                # Execute specialist agent
                result = self._execute_agent_with_retry(agent, task, context)
                workflow.results[task.task_id] = result
                self.tracker.record_execution(result)

                if result.success:
                    context.store_task_result(task.task_id, result.data)
                    workflow.add_log(f"Agent '{result.agent_name}' completed task '{task.task_id[:8]}' in {result.execution_time_ms:.2f}ms.")
                    executed_task_ids.add(task.task_id)
                else:
                    workflow.add_log(f"Agent '{result.agent_name}' failed task '{task.task_id[:8]}': {result.error_message}")
                    workflow.status = WorkflowStatus.FAILED
                    executed_task_ids.add(task.task_id)
                    break

        if all(r.success for r in workflow.results.values()):
            workflow.status = WorkflowStatus.COMPLETED
            workflow.add_log(f"Workflow '{workflow.name}' completed successfully.")
            logger.info(f"[WorkflowEngine] Workflow '{workflow.name}' execution completed cleanly.")

        return workflow

    def render_workflow_graph(self, workflow: Workflow) -> str:
        """
        Renders a ASCII text visual representation of the multi-agent workflow DAG.
        """
        lines = [f"Workflow Graph: {workflow.name} (ID: {workflow.workflow_id[:8]})", "Manager Agent"]
        for idx, task in enumerate(workflow.tasks, 1):
            agent_type = task.target_agent_type or "Specialist"
            deps = f" [After Task {', '.join(task.dependencies)}]" if task.dependencies else ""
            lines.append(f"   │")
            lines.append(f"   ├──► Step {idx}: [{agent_type}] {task.description}{deps}")
        return "\n".join(lines)

    def _execute_agent_with_retry(self, agent: Any, task: AgentTask, context: AgentContext) -> AgentResult:
        """Executes an agent with retry management on failure."""
        start_time = time.time()
        retry_count = 0
        last_error = None

        while retry_count <= task.max_retries:
            try:
                execute_func = getattr(agent, "execute")
                result = execute_func(task, context)
                if result.success or retry_count >= task.max_retries:
                    result.retry_count = retry_count
                    return result
                retry_count += 1
                logger.warning(f"[WorkflowEngine] Agent '{agent.name}' failed task '{task.task_id[:8]}'. Attempting retry {retry_count}/{task.max_retries}...")
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000.0
                last_error = str(e)
                retry_count += 1

        elapsed = (time.time() - start_time) * 1000.0
        return AgentResult(
            task_id=task.task_id,
            agent_name=getattr(agent, "name", "specialist"),
            success=False,
            error_message=last_error or "Execution retries exhausted",
            execution_time_ms=elapsed,
            retry_count=retry_count
        )
