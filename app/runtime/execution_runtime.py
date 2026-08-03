"""
Autonomous Execution Runtime Facade for Project Astra.
Master coordinator managing workflow execution, checkpointing, crash recovery, pause/resume, and timeouts.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Set

from app.ports.runtime_port import RuntimePort
from app.runtime.state_store import StateStore
from app.runtime.checkpoint_manager import CheckpointManager
from app.runtime.progress_tracker import ProgressTracker
from app.runtime.retry_policy import RetryPolicy
from app.runtime.timeout_manager import TimeoutManager
from app.runtime.workflow_scheduler import WorkflowScheduler
from app.runtime.execution_monitor import ExecutionMonitor
from app.models.workflow import Workflow
from app.models.agent_task import AgentTask
from app.models.execution_state import ExecutionState, ExecutionStatus
from app.models.execution_checkpoint import ExecutionCheckpoint
from app.models.runtime_event import RuntimeEvent, RuntimeEventType
from app.orchestrator.agent_selector import AgentSelector, agent_selector
from app.orchestrator.agent_context import AgentContext
from app.utils.logger import logger


class ExecutionRuntime:
    """
    Master Autonomous Execution Runtime for Project Astra.
    """

    def __init__(
        self,
        port: Optional[RuntimePort] = None,
        selector: Optional[AgentSelector] = None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout_sec: float = 60.0
    ):
        self.port = port or StateStore()
        self.selector = selector or agent_selector
        self.checkpoint_manager = CheckpointManager(port=self.port)
        self.retry_policy = retry_policy or RetryPolicy()
        self.timeout_manager = TimeoutManager(default_timeout_sec=timeout_sec)
        self.scheduler = WorkflowScheduler()
        self.monitor = ExecutionMonitor()
        self._active_paused_workflows: Set[str] = set()
        self._active_cancelled_workflows: Set[str] = set()

    async def execute_workflow(self, workflow: Workflow, context: Optional[AgentContext] = None) -> ExecutionState:
        """
        Executes a multi-agent DAG workflow asynchronously with checkpointing and crash recovery.
        """
        context = context or AgentContext(goal_description=workflow.goal_description)
        workflow_id = workflow.workflow_id

        # 1. Initialize or Recover ExecutionState
        state = self.port.get_state(workflow_id)
        if not state:
            state = ExecutionState(
                workflow_id=workflow_id,
                goal_description=workflow.goal_description,
                status=ExecutionStatus.RUNNING,
                total_steps=len(workflow.tasks)
            )
        else:
            state.status = ExecutionStatus.RUNNING

        self.port.save_state(state)
        self.monitor.record_event(RuntimeEvent(
            event_type=RuntimeEventType.WORKFLOW_STARTED,
            workflow_id=workflow_id,
            message=f"Started workflow '{workflow_id[:8]}'"
        ))

        completed_set = set(state.completed_step_ids)
        step_index = len(completed_set)

        # 2. Sequential / Parallel Step Execution Loop
        while len(completed_set) < len(workflow.tasks):

            # Check pause / cancel flags
            if workflow_id in self._active_paused_workflows:
                state.status = ExecutionStatus.PAUSED
                self.port.save_state(state)
                logger.info(f"[ExecutionRuntime] Workflow '{workflow_id[:8]}' PAUSED.")
                return state

            if workflow_id in self._active_cancelled_workflows:
                state.status = ExecutionStatus.CANCELLED
                self.port.save_state(state)
                logger.info(f"[ExecutionRuntime] Workflow '{workflow_id[:8]}' CANCELLED.")
                return state

            ready_tasks = self.scheduler.schedule_ready_tasks(workflow, completed_set)
            if not ready_tasks:
                if len(completed_set) < len(workflow.tasks):
                    state.status = ExecutionStatus.FAILED
                    state.error_message = "Dependency deadlock: No ready tasks available."
                    self.port.save_state(state)
                    return state
                break

            for task in ready_tasks:
                if task.task_id in completed_set:
                    continue

                state.current_step_id = task.task_id
                self.port.save_state(state)

                # Select Specialist Agent
                agent = self.selector.select_agent_for_task(task)
                if not agent:
                    state.status = ExecutionStatus.FAILED
                    state.error_message = f"No agent available for task '{task.description}'"
                    self.port.save_state(state)
                    return state

                # Execute with Retry Policy and Timeout Guardrails
                success = False
                result_data = {}
                attempt = 0

                while attempt <= self.retry_policy.max_retries and not success:
                    attempt += 1
                    try:
                        logger.info(f"[ExecutionRuntime] Executing step {step_index + 1}/{len(workflow.tasks)} ('{task.description}') via {agent.name}")

                        # Wrap in Timeout Guardrail
                        async def _exec():
                            return agent.execute(task, context)

                        result = await self.timeout_manager.execute_with_timeout(
                            _exec(),
                            timeout_sec=float(task.timeout_seconds)
                        )

                        if result.success:
                            success = True
                            result_data = result.data or {}
                        else:
                            logger.warning(f"Step failed: {result.error_message}. Retry attempt {attempt}...")
                            if attempt <= self.retry_policy.max_retries:
                                await self.retry_policy.wait_before_retry(attempt)
                    except asyncio.TimeoutError:
                        logger.error(f"Task '{task.task_id[:8]}' timed out on attempt {attempt}")
                        if attempt <= self.retry_policy.max_retries:
                            await self.retry_policy.wait_before_retry(attempt)
                    except Exception as e:
                        logger.error(f"Task execution error on attempt {attempt}: {e}")
                        if attempt <= self.retry_policy.max_retries:
                            await self.retry_policy.wait_before_retry(attempt)

                if not success:
                    state.status = ExecutionStatus.FAILED
                    state.failed_step_ids.append(task.task_id)
                    state.error_message = f"Task '{task.description}' failed after {attempt - 1} retries."
                    self.port.save_state(state)
                    return state

                # Step Success -> Save Checkpoint & Update State
                completed_set.add(task.task_id)
                state.completed_step_ids.append(task.task_id)
                state.completed_steps = len(completed_set)
                step_index += 1

                context.store_task_result(task.task_id, result_data)

                self.checkpoint_manager.create_checkpoint(
                    workflow_id=workflow_id,
                    step_id=task.task_id,
                    step_index=step_index,
                    step_result_data=result_data,
                    context_snapshot=context.to_dict()
                )
                self.port.save_state(state)

        # 3. Workflow Completed
        state.status = ExecutionStatus.COMPLETED
        state.end_time = time.time()
        self.port.save_state(state)

        self.monitor.record_event(RuntimeEvent(
            event_type=RuntimeEventType.WORKFLOW_COMPLETED,
            workflow_id=workflow_id,
            message=f"Workflow '{workflow_id[:8]}' completed successfully."
        ))

        logger.info(f"[ExecutionRuntime] Workflow '{workflow_id[:8]}' COMPLETED successfully ({state.progress_percentage}%).")
        return state

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pauses a running workflow."""
        self._active_paused_workflows.add(workflow_id)
        logger.info(f"[ExecutionRuntime] Pausing workflow '{workflow_id}'")
        return True

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resumes a paused workflow."""
        if workflow_id in self._active_paused_workflows:
            self._active_paused_workflows.remove(workflow_id)
        logger.info(f"[ExecutionRuntime] Resuming workflow '{workflow_id}'")
        return True

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancels a running workflow."""
        self._active_cancelled_workflows.add(workflow_id)
        logger.info(f"[ExecutionRuntime] Cancelling workflow '{workflow_id}'")
        return True
