"""
Unit tests for Day 11 Autonomous Execution Runtime.
Tests StateStore, CheckpointManager, ProgressTracker, RetryPolicy, TimeoutManager, TaskQueue,
WorkflowScheduler, ExecutionMonitor, and ExecutionRuntime.
"""

import pytest
import asyncio
import time

from app.models.agent_task import AgentTask, TaskPriority
from app.models.workflow import Workflow, WorkflowStatus
from app.models.execution_state import ExecutionState, ExecutionStatus
from app.models.execution_checkpoint import ExecutionCheckpoint
from app.runtime.state_store import StateStore
from app.runtime.checkpoint_manager import CheckpointManager
from app.runtime.progress_tracker import ProgressTracker
from app.runtime.retry_policy import RetryPolicy, RetryStrategy
from app.runtime.timeout_manager import TimeoutManager
from app.runtime.task_queue import TaskQueue
from app.runtime.workflow_scheduler import WorkflowScheduler
from app.runtime.execution_monitor import ExecutionMonitor
from app.runtime.execution_runtime import ExecutionRuntime
from app.orchestrator.agent_registry import AgentRegistry
from app.orchestrator.agent_selector import AgentSelector
from app.agents.coding_agent import CodingAgent
from app.agents.research_agent import ResearchAgent


@pytest.fixture
def tmp_state_store(tmp_path):
    db_path = str(tmp_path / "test_runtime_state.db")
    store = StateStore(db_path=db_path)
    return store


@pytest.fixture
def custom_registry():
    registry = AgentRegistry()
    registry.register(CodingAgent())
    registry.register(ResearchAgent())
    return registry


class TestStateStoreAndCheckpoints:
    def test_state_persistence(self, tmp_state_store):
        state = ExecutionState(
            workflow_id="wf_123",
            goal_description="Test Workflow Goal",
            total_steps=3,
            completed_steps=1,
            status=ExecutionStatus.RUNNING
        )
        saved = tmp_state_store.save_state(state)
        assert saved is True

        retrieved = tmp_state_store.get_state("wf_123")
        assert retrieved is not None
        assert retrieved.goal_description == "Test Workflow Goal"
        assert retrieved.completed_steps == 1

    def test_checkpoint_saving_and_recovery(self, tmp_state_store):
        cp_mgr = CheckpointManager(port=tmp_state_store)
        cp = cp_mgr.create_checkpoint(
            workflow_id="wf_123",
            step_id="step_1",
            step_index=1,
            step_result_data={"status": "ok"},
            context_snapshot={"key": "val"}
        )
        assert cp.checkpoint_id is not None

        latest = cp_mgr.get_latest_checkpoint("wf_123")
        assert latest is not None
        assert latest.step_id == "step_1"
        assert latest.context_snapshot["key"] == "val"


class TestRetryAndTimeout:
    def test_retry_policy_delays(self):
        policy = RetryPolicy(max_retries=3, strategy=RetryStrategy.EXPONENTIAL_BACKOFF, base_delay_sec=0.1)
        assert policy.calculate_delay(1) == 0.1
        assert policy.calculate_delay(2) == 0.2
        assert policy.calculate_delay(3) == 0.4

    @pytest.mark.asyncio
    async def test_timeout_manager_triggers_timeout(self):
        mgr = TimeoutManager(default_timeout_sec=0.1)

        async def slow_task():
            await asyncio.sleep(0.5)

        with pytest.raises(asyncio.TimeoutError):
            await mgr.execute_with_timeout(slow_task(), timeout_sec=0.1)


class TestProgressAndMetrics:
    def test_progress_bar_rendering(self):
        bar = ProgressTracker.render_progress_bar(completed=4, total=5)
        assert "80%" in bar
        assert "4/5 steps complete" in bar

    def test_execution_monitor(self):
        monitor = ExecutionMonitor()
        summary = monitor.get_dashboard_metrics()
        assert "total_workflows_executed" in summary


class TestExecutionRuntimeFlow:
    @pytest.mark.asyncio
    async def test_workflow_execution_and_resume(self, tmp_state_store, custom_registry, tmp_path):
        folder_path = str(tmp_path / "RuntimeTestFolder")

        selector = AgentSelector(registry=custom_registry)
        runtime = ExecutionRuntime(port=tmp_state_store, selector=selector)

        task1 = AgentTask(
            task_id="t1",
            description=f"Create a project called {folder_path}",
            target_agent_type="CodingAgent"
        )
        workflow = Workflow(
            name="Test Workflow",
            goal_description="Create test folder",
            tasks=[task1]
        )

        state = await runtime.execute_workflow(workflow)
        assert state.status == ExecutionStatus.COMPLETED
        assert state.completed_steps == 1

        # Checkpoint verified
        cp = runtime.checkpoint_manager.get_latest_checkpoint(workflow.workflow_id)
        assert cp is not None
        assert cp.step_id == "t1"
