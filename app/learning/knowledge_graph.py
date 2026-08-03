"""
Personal Knowledge Graph Manager for Project Astra OS.
Connects developer projects, skills, goals, preferences, and memories.
"""

from typing import Dict, List, Any, Optional
from app.models.knowledge_node import KnowledgeNode
from app.models.knowledge_edge import KnowledgeEdge


class PersonalKnowledgeGraph:
    """
    Graph Engine for Personal Knowledge Representation.
    """

    def __init__(self):
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, KnowledgeEdge] = {}
        self._init_default_graph()

    def _init_default_graph(self) -> None:
        n_user = KnowledgeNode("node-rudra", "Rudra Thakur", "user", {"role": "Lead Architect"})
        n_proj = KnowledgeNode("node-astra", "Project Astra OS", "project", {"status": "in_development"})
        n_skill = KnowledgeNode("node-python", "Python & System Design", "skill", {"level": "expert"})

        self.add_node(n_user)
        self.add_node(n_proj)
        self.add_node(n_skill)

        self.add_edge(KnowledgeEdge("edge-1", n_user.node_id, n_proj.node_id, "MAINTAINS", weight=1.0))
        self.add_edge(KnowledgeEdge("edge-2", n_user.node_id, n_skill.node_id, "HAS_SKILL", weight=1.0))

    def add_node(self, node: KnowledgeNode) -> None:
        self._nodes[node.node_id] = node

    def add_edge(self, edge: KnowledgeEdge) -> None:
        self._edges[edge.edge_id] = edge

    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()]
        }

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()
