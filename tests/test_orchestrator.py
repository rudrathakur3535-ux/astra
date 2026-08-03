"""
Unit tests for Day 8 Multi-Agent Orchestrator & Specialist Agents.
Tests BaseAgent interface, ManagerAgent, Specialist Agents (Research, Browser, Coding, Memory, Vision, Desktop, Communication),
WorkflowEngine execution, AgentContext sharing, EventBus PubSub, and AgentMetricsTracker.
"""

import pytest
from typing import List, Dict, Any

from app.models.agent_task import AgentTask, TaskPriority
from app.models.agent_result import AgentResult
from app.models.workflow import Workflow, WorkflowMode, WorkflowStatus
from app.orchestrator.agent_context import AgentContext
from app.orchestrator.event_bus import EventBus
from app.orchestrator.agent_registry import AgentRegistry
from app.orchestrator.agent_selector import AgentSelector
from app.orchestrator.metrics_tracker import AgentMetricsTracker
from app.orchestrator.workflow_engine import WorkflowEngine
from app.orchestrator.orchestrator import MultiAgentOrchestrator

from app.agents.manager_agent import ManagerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.browser_agent import BrowserAgent
from app.agents.coding_agent import CodingAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.vision_agent import VisionAgent
from app.agents.desktop_agent import DesktopAgent
from app.agents.communication_agent import CommunicationAgent


@pytest.fixture
def custom_registry():
    registry = AgentRegistry()
    registry.register(ManagerAgent())
    registry.register(ResearchAgent())
    registry.register(BrowserAgent())
    registry.register(CodingAgent())
    registry.register(MemoryAgent())
    registry.register(VisionAgent())
    registry.register(DesktopAgent())
    registry.register(CommunicationAgent())
    return registry


class TestAgentRegistryAndSelector:
    def test_agent_discovery(self, custom_registry):
        selector = AgentSelector(registry=custom_registry)
        task = AgentTask(description="Research LangGraph tutorials", target_agent_type="ResearchAgent")

        selected = selector.select_agent_for_task(task)
        assert selected is not None
        assert selected.name == "ResearchAgent"

    def test_can_handle_matching(self, custom_registry):
        selector = AgentSelector(registry=custom_registry)
        task = AgentTask(description="Create project directory FinanceAI")

        selected = selector.select_agent_for_task(task)
        assert selected is not None
        assert selected.name in ("CodingAgent", "DesktopAgent", "ManagerAgent")


class TestEventBus:
    def test_pubsub_event_messaging(self):
        bus = EventBus()
        received_events = []

        def on_event(topic: str, payload: Any):
            received_events.append((topic, payload))

        bus.subscribe("RESEARCH_COMPLETED", on_event)
        bus.publish("RESEARCH_COMPLETED", {"query": "LangGraph"})

        assert len(received_events) == 1
        assert received_events[0][0] == "RESEARCH_COMPLETED"
        assert received_events[0][1]["query"] == "LangGraph"


class TestAgentContext:
    def test_shared_context_state(self):
        context = AgentContext(goal_description="Test Goal")
        context.set("user_name", "Rudra")
        context.store_task_result("task123", {"status": "ok"})
        context.add_artifact("C:/logs/screenshot.png")

        assert context.get("user_name") == "Rudra"
        assert context.get_task_result("task123") == {"status": "ok"}
        assert len(context.list_artifacts()) == 1


class TestMetricsTracker:
    def test_metrics_recording_and_dashboard_summary(self):
        tracker = AgentMetricsTracker()
        res1 = AgentResult(task_id="t1", agent_name="BrowserAgent", success=True, execution_time_ms=100.0)
        res2 = AgentResult(task_id="t2", agent_name="BrowserAgent", success=True, execution_time_ms=200.0)
        res3 = AgentResult(task_id="t3", agent_name="CodingAgent", success=False, execution_time_ms=150.0)

        tracker.record_execution(res1)
        tracker.record_execution(res2)
        tracker.record_execution(res3)

        summary = tracker.get_dashboard_summary()
        assert summary["total_tasks_processed"] == 3
        assert summary["most_used_agent"] == "BrowserAgent"
        assert "BrowserAgent" in summary["agent_performance"]
        assert summary["agent_performance"]["BrowserAgent"]["avg_latency_ms"] == 150.0


class TestMultiAgentOrchestratorFlow:
    def test_full_multi_agent_workflow(self, custom_registry, tmp_path):
        folder_name = str(tmp_path / "MultiAgentFinanceAI")

        selector = AgentSelector(registry=custom_registry)
        tracker = AgentMetricsTracker()
        engine = WorkflowEngine(selector=selector, tracker=tracker)
        bus = EventBus()
        orchestrator = MultiAgentOrchestrator(
            registry=custom_registry,
            selector=selector,
            engine=engine,
            bus=bus,
            tracker=tracker
        )

        manager = ManagerAgent()
        workflow_data = orchestrator.execute_goal_workflow(
            goal_description=f"Create a project called {folder_name}",
            manager_agent=manager
        )

        assert workflow_data["status"] == WorkflowStatus.COMPLETED.value
        assert workflow_data["tasks_total"] >= 1
        assert "graph_visualization" in workflow_data
        assert "metrics" in workflow_data
