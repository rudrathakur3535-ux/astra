"""
Planner Engine & Plan Cache for Project Astra.
Translates natural language goals into structured multi-step execution plans.
Includes PlanCache for reusing past successful step sequences for recurring goals.
"""

from typing import Dict, Any, List, Optional
import json
import re

from app.ports.planner_port import PlannerPort
from app.models.goal import Goal
from app.models.plan import Plan, PlanStatus
from app.models.plan_step import PlanStep, StepStatus
from app.tools.tool_registry import tool_registry
from app.utils.logger import logger


class PlanCache:
    """
    In-memory and file cache for storing and reusing successful plan sequences for recurring goals.
    """

    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def _normalize_key(self, goal_text: str) -> str:
        return re.sub(r"[^\w\s]", "", goal_text.strip().lower())

    def get_plan(self, goal_text: str) -> Optional[List[Dict[str, Any]]]:
        key = self._normalize_key(goal_text)
        return self._cache.get(key)

    def store_plan(self, goal_text: str, steps: List[PlanStep]) -> None:
        key = self._normalize_key(goal_text)
        self._cache[key] = [s.to_dict() for s in steps]
        logger.info(f"Cached successful plan sequence for goal pattern: '{key}'")


class PlannerEngine(PlannerPort):
    """
    Translates natural language goals into structured execution plans.
    """

    def __init__(self, plan_cache: Optional[PlanCache] = None):
        self.plan_cache = plan_cache or PlanCache()

    async def evaluate_step(self, step: PlanStep, step_result: str) -> bool:
        return True

    def create_plan(self, goal: Any) -> Plan:
        """
        Generates a multi-step Plan for a given user Goal.

        Checks PlanCache first for recurring goal patterns.
        """
        goal_text = goal.description if hasattr(goal, "description") else str(goal)
        logger.info(f"Generating execution plan for Goal: '{goal_text}'")

        # 1. Check PlanCache
        cached_steps_data = self.plan_cache.get_plan(goal_text)
        if cached_steps_data:
            logger.info(f"PlanCache hit for goal: '{goal_text}'")
            steps = [PlanStep.from_dict(d) for d in cached_steps_data]
            plan = Plan(goal=goal_text, steps=steps)
            return plan

        # 2. Heuristic / Rule-based Planner for common Astra goals
        steps = self._generate_heuristic_steps(goal_text)

        plan = Plan(goal=goal_text, steps=steps)
        return plan

    def validate_plan(self, plan: Plan) -> bool:
        from app.planning.plan_validator import PlanValidator
        validator = PlanValidator()
        is_valid, _ = validator.validate(plan)
        return is_valid


    def _generate_heuristic_steps(self, goal_text: str) -> List[PlanStep]:
        """
        Decomposes common Astra goals into structured plan steps.
        """
        text = goal_text.lower()
        steps: List[PlanStep] = []

        # Example 1: YouTube Search (e.g. "Open YouTube and search for LangGraph tutorials")
        if "youtube" in text and "search" in text:
            # Extract search query
            query = "LangGraph tutorials"
            if "for" in text:
                query = goal_text.split("for")[-1].strip()

            steps.append(PlanStep(
                id=1,
                tool="browser.youtube_search",
                args={"query": query},
                description=f"Search YouTube for '{query}'",
                expected_outcome="YouTube search results page loaded"
            ))
            steps.append(PlanStep(
                id=2,
                tool="browser.page_title",
                args={},
                description="Verify YouTube page title",
                dependencies=[1],
                expected_outcome="Title containing YouTube"
            ))

        # Example 2: Project Creation (e.g. "Create a project called FinanceAI")
        elif "create" in text and ("project" in text or "folder" in text):
            folder_name = "FinanceAI"
            words = goal_text.split()
            if words:
                folder_name = words[-1].strip(".")

            steps.append(PlanStep(
                id=1,
                tool="create_folder",
                args={"folder_name": folder_name},
                description=f"Create project folder '{folder_name}'",
                expected_outcome=f"Folder '{folder_name}' created"
            ))
            steps.append(PlanStep(
                id=2,
                tool="open_folder",
                args={"folder_path": folder_name},
                description=f"Open folder '{folder_name}' in Windows Explorer",
                dependencies=[1],
                expected_outcome=f"Folder '{folder_name}' opened"
            ))

        # Example 3: Web Research (e.g. "Research RAG" or "Google search LangGraph")
        elif "research" in text or "google" in text:
            query = "RAG retrieval augmented generation"
            if "research" in text:
                query = goal_text.replace("research", "").strip()
            elif "search" in text:
                query = goal_text.split("search")[-1].strip()

            steps.append(PlanStep(
                id=1,
                tool="browser.google_search",
                args={"query": query},
                description=f"Google search for '{query}'",
                expected_outcome="Google search results page loaded",
                fallback_tool="browser.github_search"  # Self-correction fallback
            ))
            steps.append(PlanStep(
                id=2,
                tool="browser.read_page",
                args={},
                description="Extract page summary content",
                dependencies=[1],
                expected_outcome="Page text content extracted"
            ))

        # Fallback default: Open URL or System Info
        else:
            steps.append(PlanStep(
                id=1,
                tool="get_system_info",
                args={},
                description="Check system metrics",
                expected_outcome="RAM and CPU metrics returned"
            ))

        return steps
