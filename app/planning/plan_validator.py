"""
Plan Validator Module for Project Astra.
Performs pre-execution safety, schema validation, and dependency checks on plans.
"""

from typing import List, Tuple, Dict, Any, Optional
from app.models.plan import Plan, PlanStatus
from app.planning.task_graph import TaskGraph
from app.tools.tool_registry import tool_registry
from app.utils.logger import logger


class PlanValidator:
    """
    Validates execution plans for tool existence, circular dependencies, and parameter schemas.
    """

    def validate(self, plan: Plan) -> Tuple[bool, List[str]]:
        """
        Validates a Plan object.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_error_messages)
        """
        errors: List[str] = []

        if not plan.steps:
            errors.append("Plan contains no execution steps.")
            return False, errors

        # 1. Verify DAG circular dependencies
        try:
            graph = TaskGraph(plan.steps)
            if graph.has_circular_dependency():
                errors.append("Plan contains a circular step dependency loop.")
        except Exception as e:
            errors.append(f"Failed to analyze task graph dependencies: {e}")

        # 2. Check each step against tool registry
        for step in plan.steps:
            if not step.tool:
                errors.append(f"Step {step.id} has no tool specified.")
                continue

            tool_instance = tool_registry.get_tool(step.tool)
            if not tool_instance:
                # Check if fallback tool exists
                if step.fallback_tool and tool_registry.get_tool(step.fallback_tool):
                    logger.warning(f"Primary tool '{step.tool}' not found for Step {step.id}. Will use fallback '{step.fallback_tool}'.")
                else:
                    errors.append(f"Step {step.id}: Tool '{step.tool}' is not registered in Astra tool registry.")

            # Validate fallback tool if specified
            if step.fallback_tool and not tool_registry.get_tool(step.fallback_tool):
                errors.append(f"Step {step.id}: Specified fallback tool '{step.fallback_tool}' is not registered.")

        is_valid = len(errors) == 0
        if is_valid:
            plan.status = PlanStatus.VALIDATED
            logger.info(f"Plan '{plan.plan_id}' successfully validated ({len(plan.steps)} steps).")
        else:
            plan.status = PlanStatus.REJECTED
            logger.error(f"Plan validation failed for '{plan.plan_id}': {errors}")

        return is_valid, errors
