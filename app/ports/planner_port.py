from abc import ABC, abstractmethod
from app.models.plan import Plan, PlanStep

class BasePlannerPort(ABC):
    @abstractmethod
    async def create_plan(self, user_goal: str) -> Plan:
        pass

    @abstractmethod
    async def evaluate_step(self, step: PlanStep, step_result: str) -> bool:
        pass

# Alias for backwards compatibility
PlannerPort = BasePlannerPort
