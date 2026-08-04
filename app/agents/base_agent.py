from abc import ABC, abstractmethod
from app.models.agent_task import AgentTask
from app.models.agent_result import AgentResult

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        pass
