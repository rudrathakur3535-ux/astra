"""
Workflow DAG & Live Agent Graph Visualizer for Project Astra OS.
Generates directed graph topologies (nodes & edges) for workflows and active agent interactions.
"""

from typing import Dict, List, Any, Optional
from app.models.trace import TraceSpan


class WorkflowVisualizer:
    """
    Generates DAG execution graphs and agent interaction topologies for developer dashboards.
    """

    def generate_workflow_dag(self, spans: List[TraceSpan]) -> Dict[str, Any]:
        """
        Transforms a list of trace spans into a DAG node-and-edge graph structure.
        """
        if not spans:
            return {"nodes": [], "edges": [], "root_id": None}

        sorted_spans = sorted(spans, key=lambda s: s.start_time)
        root_span = next((s for s in sorted_spans if s.parent_span_id is None), sorted_spans[0])

        nodes = []
        edges = []

        for span in sorted_spans:
            nodes.append({
                "id": span.span_id,
                "label": span.operation_name,
                "status": span.status.value if hasattr(span.status, "value") else str(span.status),
                "duration_ms": span.duration_ms,
                "start_time": span.start_time,
                "tags": span.tags
            })

            if span.parent_span_id:
                edges.append({
                    "from": span.parent_span_id,
                    "to": span.span_id,
                    "label": "child_operation"
                })

        # Add implicit sequential edges if no explicit parent links exist
        if len(edges) == 0 and len(nodes) > 1:
            for i in range(len(nodes) - 1):
                edges.append({
                    "from": nodes[i]["id"],
                    "to": nodes[i + 1]["id"],
                    "label": "sequence"
                })

        return {
            "root_id": root_span.span_id,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes)
        }

    def generate_live_agent_graph(self, active_agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a topology of currently active agents and inter-agent communication channels.
        Example active_agents: [{"name": "Planner", "target": "Research Agent", "status": "running"}]
        """
        nodes = []
        edges = []
        seen_agents = set()

        for item in active_agents:
            agent_name = item.get("name", "UnknownAgent")
            target_name = item.get("target")
            status = item.get("status", "active")

            if agent_name not in seen_agents:
                seen_agents.add(agent_name)
                nodes.append({"id": agent_name, "label": agent_name, "type": "agent", "status": status})

            if target_name:
                if target_name not in seen_agents:
                    seen_agents.add(target_name)
                    nodes.append({"id": target_name, "label": target_name, "type": "subsystem_or_agent", "status": "active"})

                edges.append({
                    "from": agent_name,
                    "to": target_name,
                    "label": item.get("interaction", "delegates")
                })

        # Default standard multi-agent topology if empty
        if not nodes:
            default_flow = ["Planner Agent", "Research Agent", "Browser Agent", "Knowledge Engine", "LLM Core", "Execution Response"]
            for name in default_flow:
                nodes.append({"id": name, "label": name, "type": "agent", "status": "idle"})
            for i in range(len(default_flow) - 1):
                edges.append({"from": default_flow[i], "to": default_flow[i + 1], "label": "flow"})

        return {
            "nodes": nodes,
            "edges": edges,
            "active_count": len(seen_agents)
        }
