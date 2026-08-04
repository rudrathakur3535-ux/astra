from enum import Enum
from typing import Optional, List
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
    step_id: int
    title: str
    instruction: str
    target_tool_or_agent: str
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None

class Plan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    steps: List[PlanStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_complete: bool = False
