import pytest
from app.models import (
    AgentTask, TaskStatus, TaskPriority,
    AvatarState, ExpressionEnum, GestureEnum,
    MemoryRecord, MemoryType,
    Plan, PlanStep, StepStatus,
    SecurityEvent, RiskLevel
)

def test_agent_task_defaults():
    task = AgentTask(
        title="Analyze Code",
        description="Run AST parser on app/main.py",
        target_agent="coding_agent",
        priority=TaskPriority.HIGH
    )
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.HIGH
    assert task.target_agent == "coding_agent"

def test_avatar_state_defaults():
    avatar = AvatarState(
        expression=ExpressionEnum.SMILE,
        gesture=GestureEnum.WAVE,
        is_speaking=True
    )
    assert avatar.expression == ExpressionEnum.SMILE
    assert avatar.gesture == GestureEnum.WAVE
    assert avatar.is_speaking is True

def test_security_event_model():
    event = SecurityEvent(
        event_id="sec-001",
        action="exec_shell",
        risk_level=RiskLevel.CRITICAL,
        user_confirmed=False
    )
    assert event.risk_level == RiskLevel.CRITICAL
    assert event.user_confirmed is False
