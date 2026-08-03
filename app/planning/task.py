"""
Task Node Module for Project Astra.
Wraps PlanStep with DAG parent/child relationship pointers for graph traversal.
"""

from typing import List
from app.models.plan_step import PlanStep


class TaskNode:
    """
    Graph node wrapping a PlanStep with parent and child dependencies.
    """

    def __init__(self, step: PlanStep):
        self.step = step
        self.parents: List["TaskNode"] = []
        self.children: List["TaskNode"] = []

    @property
    def step_id(self) -> int:
        return self.step.id

    def is_ready(self) -> bool:
        """Returns True if all parent steps have executed successfully."""
        from app.models.plan_step import StepStatus
        return all(p.step.status == StepStatus.SUCCESS for p in self.parents)
