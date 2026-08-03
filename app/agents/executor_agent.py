"""
Executor Agent for Project Astra.
Drives plan execution through TaskExecutor using dependency-ordered graph traversal.
"""

from typing import Optional, Dict, Any, List
from app.models.plan import Plan, PlanStatus
from app.models.plan_step import PlanStep, StepStatus
from app.planning.task_executor import TaskExecutor
from app.planning.task_graph import TaskGraph
from app.utils.logger import logger


class ExecutorAgent:
    """
    Executor Agent manages step-by-step plan execution loop.
    """

    def __init__(self, task_executor: Optional[TaskExecutor] = None):
        self.executor = task_executor or TaskExecutor()

    def execute_plan(self, plan: Plan) -> Plan:
        """
        Executes all steps in a validated Plan according to DAG dependencies.
        """
        if plan.status != PlanStatus.VALIDATED:
            logger.warning(f"[ExecutorAgent] Plan '{plan.plan_id}' is not in VALIDATED state (Current: {plan.status}). Proceeding with caution.")

        plan.status = PlanStatus.EXECUTING
        plan.add_log("Starting plan execution...")
        logger.info(f"[ExecutorAgent] Starting execution for Plan '{plan.plan_id}'")

        graph = TaskGraph(plan.steps)

        while True:
            ready_steps = graph.get_executable_steps()
            if not ready_steps:
                break

            for step in ready_steps:
                plan.add_log(f"Executing step {step.id} ({step.tool})...")
                response = self.executor.execute_step(step)

                if response.success:
                    plan.add_log(f"Step {step.id} completed successfully.")
                else:
                    plan.add_log(f"Step {step.id} failed: {response.error_message}")
                    logger.error(f"[ExecutorAgent] Step {step.id} failed. Halting plan progression.")

                    # Mark dependent steps as SKIPPED
                    for s in plan.steps:
                        if s.status == StepStatus.PENDING and step.id in s.dependencies:
                            s.status = StepStatus.SKIPPED
                            plan.add_log(f"Step {s.id} skipped due to failed dependency Step {step.id}.")
                    break

        if plan.is_complete:
            plan.status = PlanStatus.COMPLETED
            plan.add_log("Plan execution completed successfully.")
            logger.info(f"[ExecutorAgent] Plan '{plan.plan_id}' execution completed cleanly.")
        else:
            plan.status = PlanStatus.FAILED
            plan.add_log("Plan execution finished with failures.")
            logger.warning(f"[ExecutorAgent] Plan '{plan.plan_id}' execution finished with errors.")

        return plan
