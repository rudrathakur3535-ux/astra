"""
Unit tests for Day 7 Agentic AI & Task Planning Engine.
Tests Plan generation, TaskGraph DAG sorting, PlanValidator, TaskExecutor retries,
self-correction fallbacks, VerificationAgent, ReflectionAgent, and PlanCache.
"""

import pytest
import os
from typing import List

from app.models.goal import Goal
from app.models.plan import Plan, PlanStatus
from app.models.plan_step import PlanStep, StepStatus
from app.planning.task import TaskNode
from app.planning.task_graph import TaskGraph
from app.planning.plan_validator import PlanValidator
from app.planning.task_executor import TaskExecutor
from app.planning.planner import PlannerEngine, PlanCache
from app.agents.planner_agent import PlannerAgent
from app.agents.executor_agent import ExecutorAgent
from app.agents.verification_agent import VerificationAgent
from app.agents.reflection_agent import ReflectionAgent


class TestTaskGraph:
    def test_topological_sort_and_parallel_steps(self):
        steps = [
            PlanStep(id=1, tool="create_folder", args={"folder_name": "TestDir"}),
            PlanStep(id=2, tool="get_system_info", args={}),
            PlanStep(id=3, tool="open_folder", args={"folder_path": "TestDir"}, dependencies=[1])
        ]
        graph = TaskGraph(steps)
        assert graph.has_circular_dependency() is False

        ready = graph.get_executable_steps()
        assert len(ready) == 2
        ready_ids = [s.id for s in ready]
        assert 1 in ready_ids
        assert 2 in ready_ids

    def test_circular_dependency_detection(self):
        steps = [
            PlanStep(id=1, tool="toolA", dependencies=[2]),
            PlanStep(id=2, tool="toolB", dependencies=[1])
        ]
        graph = TaskGraph(steps)
        assert graph.has_circular_dependency() is True


class TestPlanValidator:
    def test_validate_valid_plan(self):
        plan = Plan(
            goal=Goal(description="Test valid plan"),
            steps=[PlanStep(id=1, tool="get_system_info", args={})]
        )
        validator = PlanValidator()
        is_valid, errors = validator.validate(plan)
        assert is_valid is True
        assert len(errors) == 0
        assert plan.status == PlanStatus.VALIDATED

    def test_validate_unregistered_tool(self):
        plan = Plan(
            goal=Goal(description="Test invalid tool"),
            steps=[PlanStep(id=1, tool="nonexistent_fake_tool_xyz", args={})]
        )
        validator = PlanValidator()
        is_valid, errors = validator.validate(plan)
        assert is_valid is False
        assert "nonexistent_fake_tool_xyz" in errors[0]


class TestPlanCache:
    def test_cache_store_and_retrieve(self):
        cache = PlanCache()
        steps = [PlanStep(id=1, tool="get_system_info", args={})]
        cache.store_plan("Check system metrics", steps)

        retrieved = cache.get_plan("Check system metrics!")
        assert retrieved is not None
        assert len(retrieved) == 1
        assert retrieved[0]["tool"] == "get_system_info"


class TestAgentOrchestrationFlow:
    def test_full_agentic_planning_pipeline(self, tmp_path):
        folder_name = str(tmp_path / "AgenticTestFolder")

        # 1. PlannerAgent
        planner_agent = PlannerAgent()
        plan, is_valid = planner_agent.plan_goal("Create project folder AgenticTestFolder")
        assert is_valid is True
        assert len(plan.steps) > 0

        # Adjust folder path to tmp_path for test isolation
        plan.steps[0].args["folder_name"] = folder_name
        plan.steps[1].args["folder_path"] = folder_name

        # 2. ExecutorAgent
        executor_agent = ExecutorAgent()
        executed_plan = executor_agent.execute_plan(plan)
        assert executed_plan.status == PlanStatus.COMPLETED

        # 3. VerificationAgent
        verifier = VerificationAgent()
        verified, details = verifier.verify_step_outcome(plan.steps[0])
        assert verified is True
        assert "exists on disk" in details

        # 4. ReflectionAgent
        reflector = ReflectionAgent(verification_agent=verifier)
        reflection = reflector.reflect_on_plan(executed_plan)
        assert reflection["goal_achieved"] is True
        assert reflection["recommendation"] == "SUCCESS"


class TestSelfCorrectionAndFallback:
    def test_task_executor_fallback_tool(self):
        executor = TaskExecutor()

        # Step with non-existent primary tool but valid fallback tool
        step = PlanStep(
            id=1,
            tool="nonexistent_primary_tool",
            args={},
            fallback_tool="get_system_info",
            fallback_args={}
        )
        response = executor.execute_step(step)
        assert response.success is True
        assert step.status == StepStatus.SUCCESS
