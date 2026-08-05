from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class PlanStep(BaseModel):
    step_id: int = 1
    title: str = ""
    instruction: str = ""
    target_tool_or_agent: str = ""
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None

    def __init__(self, **data):
        if "id" in data and "step_id" not in data:
            data["step_id"] = data.pop("id")
        if "tool" in data and "target_tool_or_agent" not in data:
            data["target_tool_or_agent"] = data.pop("tool")
        if "action" in data and "instruction" not in data:
            data["instruction"] = data.pop("action")
        super().__init__(**data)

    @property
    def id(self) -> int:
        return self.step_id

    @property
    def tool(self) -> str:
        return self.target_tool_or_agent

class Plan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    steps: List[Any] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_complete: bool = False


    def __init__(self, **data):
        if "goal" in data and not isinstance(data["goal"], str):
            data["goal"] = getattr(data["goal"], "description", str(data["goal"]))
        super().__init__(**data)

PlanStatus = StepStatus
