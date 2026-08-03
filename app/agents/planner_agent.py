"""
Planner Agent for Project Astra.
Converts user intent into structured, validated execution plans.
"""

from typing import Optional, Tuple
from app.models.goal import Goal
from app.models.plan import Plan, PlanStatus
from app.planning.planner import PlannerEngine
from app.planning.plan_validator import PlanValidator
from app.utils.logger import logger


class PlannerAgent:
    """
    Planner Agent orchestrates goal parsing, plan synthesis, and safety validation.
    """

    def __init__(self, planner_engine: Optional[PlannerEngine] = None, validator: Optional[PlanValidator] = None):
        self.planner_engine = planner_engine or PlannerEngine()
        self.validator = validator or PlanValidator()

    def plan_goal(self, goal_description: str) -> Tuple[Plan, bool]:
        """
        Accepts a natural language goal description and generates a validated Plan.

        Returns:
            Tuple[Plan, bool]: (plan_object, is_valid_and_ready)
        """
        goal = Goal(description=goal_description)
        logger.info(f"[PlannerAgent] Received Goal: '{goal_description}'")

        plan = self.planner_engine.create_plan(goal)
        is_valid, errors = self.validator.validate(plan)

        if is_valid:
            logger.info(f"[PlannerAgent] Goal '{goal_description}' successfully planned and validated ({len(plan.steps)} steps).")
        else:
            logger.error(f"[PlannerAgent] Goal planning failed validation: {errors}")
            plan.add_log(f"Validation failed: {', '.join(errors)}")

        return plan, is_valid
