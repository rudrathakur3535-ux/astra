"""
Planner Port Interface for Project Astra (Hexagonal Architecture).
Enforces decoupling between goal planning abstractions and execution agents.
"""

from abc import ABC, abstractmethod
from app.models.goal import Goal
from app.models.plan import Plan


class PlannerPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Planning Engines.
    """

    @abstractmethod
    def create_plan(self, goal: Goal) -> Plan:
        """Translates a user goal into a multi-step execution plan."""
        pass

    @abstractmethod
    def validate_plan(self, plan: Plan) -> bool:
        """Validates that all steps in a plan are safe, valid, and executable."""
        pass
