"""
Workflow Scheduler Module for Project Astra.
Schedules sequential and parallel agent tasks by resolving DAG dependencies.
"""

from typing import List, Set, Dict, Any, Optional
from app.models.agent_task import AgentTask
from app.models.workflow import Workflow, WorkflowMode
from app.runtime.task_queue import TaskQueue
from app.utils.logger import logger


class WorkflowScheduler:
    """
    Schedules workflow tasks according to dependency constraints and execution mode.
    """

    def __init__(self, queue: Optional[TaskQueue] = None):
        self.queue = queue or TaskQueue()

    def schedule_ready_tasks(self, workflow: Workflow, completed_step_ids: Set[str]) -> List[AgentTask]:
        """
        Identifies tasks whose dependencies are satisfied and pushes them into TaskQueue.
        """
        ready_tasks: List[AgentTask] = []

        for task in workflow.tasks:
            if task.task_id in completed_step_ids:
                continue

            # Check if all prerequisite dependencies are satisfied
            deps_met = all(dep in completed_step_ids for dep in task.dependencies)
            if deps_met:
                ready_tasks.append(task)
                self.queue.push(task)

        logger.info(f"[WorkflowScheduler] Scheduled {len(ready_tasks)} ready tasks for workflow '{workflow.workflow_id[:8]}'")
        return ready_tasks
