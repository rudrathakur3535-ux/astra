"""
Multi-Agent Orchestrator Module for Project Astra.
Master coordinator unifying ManagerAgent, AgentRegistry, AgentSelector, WorkflowEngine, EventBus, and MetricsTracker.
"""

from typing import Dict, Any, Optional
from app.models.workflow import Workflow, WorkflowStatus
from app.orchestrator.agent_context import AgentContext
from app.orchestrator.agent_registry import AgentRegistry, agent_registry
from app.orchestrator.agent_selector import AgentSelector, agent_selector
from app.orchestrator.workflow_engine import WorkflowEngine
from app.orchestrator.event_bus import EventBus, event_bus
from app.orchestrator.metrics_tracker import AgentMetricsTracker, metrics_tracker
from app.utils.logger import logger


class MultiAgentOrchestrator:
    """
    Central multi-agent coordinator for Project Astra OS.
    """

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        selector: Optional[AgentSelector] = None,
        engine: Optional[WorkflowEngine] = None,
        bus: Optional[EventBus] = None,
        tracker: Optional[AgentMetricsTracker] = None
    ):
        self.registry = registry or agent_registry
        self.selector = selector or agent_selector
        self.tracker = tracker or metrics_tracker
        self.engine = engine or WorkflowEngine(selector=self.selector, tracker=self.tracker)
        self.event_bus = bus or event_bus

    def execute_goal_workflow(self, goal_description: str, manager_agent: Optional[Any] = None) -> Dict[str, Any]:
        """
        Main entrypoint: Accepts user goal, generates multi-agent workflow via ManagerAgent, and executes it.
        """
        logger.info(f"[MultiAgentOrchestrator] Dispatching Goal: '{goal_description}'")

        context = AgentContext(goal_description=goal_description, event_bus=self.event_bus)

        # Generate workflow via ManagerAgent if provided, or build default workflow
        if manager_agent and hasattr(manager_agent, "create_workflow_for_goal"):
            workflow = manager_agent.create_workflow_for_goal(goal_description)
        else:
            from app.agents.manager_agent import ManagerAgent
            manager = ManagerAgent()
            workflow = manager.create_workflow_for_goal(goal_description)

        # Render ASCII graph visualization
        graph_ascii = self.engine.render_workflow_graph(workflow)
        logger.info(f"[MultiAgentOrchestrator]\n{graph_ascii}")

        # Execute multi-agent workflow
        executed_workflow = self.engine.execute_workflow(workflow, context)

        metrics = self.tracker.get_dashboard_summary()

        return {
            "workflow_id": executed_workflow.workflow_id,
            "status": executed_workflow.status.value,
            "goal": goal_description,
            "tasks_total": len(executed_workflow.tasks),
            "graph_visualization": graph_ascii,
            "context_output": context.to_dict(),
            "logs": executed_workflow.logs,
            "metrics": metrics
        }
