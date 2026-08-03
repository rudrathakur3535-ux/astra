"""
Task Executor Module for Project Astra.
Executes plan steps strictly through ToolRouter, enforcing permissions, retries, and fallback tool self-correction.
"""

from typing import Optional, Dict, Any
from app.models.plan_step import PlanStep, StepStatus
from app.models.tool_response import ToolResponse
from app.tools.tool_router import tool_router, ToolRouter
from app.utils.logger import logger


class TaskExecutor:
    """
    Executes PlanStep objects through ToolRouter with retry and self-correction support.
    """

    def __init__(self, router: Optional[ToolRouter] = None):
        self.router = router or tool_router

    def execute_step(self, step: PlanStep) -> ToolResponse:
        """
        Executes a single plan step.

        If primary tool fails, attempts step retries and fallback tool execution.
        """
        step.status = StepStatus.RUNNING
        logger.info(f"Executing Step {step.id}: Tool='{step.tool}', Args={step.args}")

        response = self.router.execute({"tool_name": step.tool, "arguments": step.args})

        # Retry logic for recoverable errors
        while not response.success and step.retry_count < step.max_retries:
            step.retry_count += 1
            step.status = StepStatus.RETRYING
            logger.warning(f"Step {step.id} failed ({response.error_message}). Attempting retry {step.retry_count}/{step.max_retries}...")
            response = self.router.execute({"tool_name": step.tool, "arguments": step.args})

        # Self-correction: Fallback tool execution if primary tool continues to fail
        if not response.success and step.fallback_tool:
            logger.warning(f"Step {step.id} primary tool '{step.tool}' failed. Triggering self-correction fallback tool '{step.fallback_tool}'...")
            fallback_args = step.fallback_args if step.fallback_args is not None else step.args
            response = self.router.execute({"tool_name": step.fallback_tool, "arguments": fallback_args})
            if response.success:
                logger.info(f"Step {step.id} self-correction successful via fallback tool '{step.fallback_tool}'.")

        # Update step state
        if response.success:
            step.status = StepStatus.SUCCESS
            step.result = response.data
            step.error_message = None
        else:
            step.status = StepStatus.FAILED
            step.result = None
            step.error_message = response.error_message

        return response
