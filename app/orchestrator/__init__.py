"""
Orchestrator Package for Project Astra.
Multi-agent workflow execution engine, discovery registry, shared context, event bus, and performance metrics tracker.
"""

from app.orchestrator.agent_context import AgentContext
from app.orchestrator.event_bus import EventBus, event_bus
from app.orchestrator.agent_registry import AgentRegistry, agent_registry
from app.orchestrator.agent_selector import AgentSelector, agent_selector
from app.orchestrator.metrics_tracker import AgentMetricsTracker, metrics_tracker
from app.orchestrator.workflow_engine import WorkflowEngine
from app.orchestrator.orchestrator import MultiAgentOrchestrator

__all__ = [
    "AgentContext",
    "EventBus",
    "event_bus",
    "AgentRegistry",
    "agent_registry",
    "AgentSelector",
    "agent_selector",
    "AgentMetricsTracker",
    "metrics_tracker",
    "WorkflowEngine",
    "MultiAgentOrchestrator"
]
