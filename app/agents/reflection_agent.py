"""
Reflection Agent for Project Astra.
Evaluates goal completion post-execution, triggers self-correction, and updates PlanCache.
"""

from typing import Dict, Any, Optional
from app.models.plan import Plan, PlanStatus
from app.agents.verification_agent import VerificationAgent
from app.planning.planner import PlanCache
from app.utils.logger import logger


class ReflectionAgent:
    """
    Reflection Agent reviewing execution results, caching successful workflows, and guiding recovery.
    """

    def __init__(self, verification_agent: Optional[VerificationAgent] = None, plan_cache: Optional[PlanCache] = None):
        self.verifier = verification_agent or VerificationAgent()
        self.plan_cache = plan_cache

    def reflect_on_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Analyzes plan outcomes and determines overall goal success or recovery action.

        Returns:
            Dict containing:
                - 'goal_achieved': bool
                - 'summary': str
                - 'recommendation': str ('SUCCESS', 'RETRY', 'ASK_USER')
                - 'verified_steps': int
        """
        logger.info(f"[ReflectionAgent] Reflecting on Plan '{plan.plan_id}' for Goal: '{plan.goal.description}'")

        verified_count = 0
        failed_steps = []

        for step in plan.steps:
            verified, details = self.verifier.verify_step_outcome(step)
            if verified:
                verified_count += 1
            else:
                failed_steps.append((step, details))

        total_steps = len(plan.steps)
        goal_achieved = plan.status == PlanStatus.COMPLETED and len(failed_steps) == 0

        if goal_achieved:
            summary = f"Goal '{plan.goal.description}' achieved successfully! ({verified_count}/{total_steps} steps verified)."
            recommendation = "SUCCESS"
            logger.info(f"[ReflectionAgent] {summary}")

            # Store successful plan in PlanCache for future instant reuse
            if self.plan_cache and plan.steps:
                self.plan_cache.store_plan(plan.goal.description, plan.steps)

        elif len(failed_steps) > 0:
            failed_desc = "; ".join([f"Step {s.id} ({s.tool}): {d}" for s, d in failed_steps])
            summary = f"Goal '{plan.goal.description}' was not fully achieved. Failed: {failed_desc}"

            # Check if failures have fallbacks available
            recoverable = any(s.fallback_tool is not None for s, _ in failed_steps)
            recommendation = "RETRY" if recoverable else "ASK_USER"
            logger.warning(f"[ReflectionAgent] {summary} | Recommendation: {recommendation}")

        else:
            summary = f"Plan completed with status {plan.status}."
            recommendation = "ASK_USER"

        return {
            "goal_achieved": goal_achieved,
            "summary": summary,
            "recommendation": recommendation,
            "verified_steps": verified_count,
            "total_steps": total_steps
        }
