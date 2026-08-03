"""
Task Graph Module for Project Astra.
Builds Directed Acyclic Graphs (DAG), detects circular dependencies, and identifies parallel steps.
"""

from typing import List, Dict, Set, Any
from app.models.plan_step import PlanStep, StepStatus
from app.planning.task import TaskNode
from app.utils.logger import logger


class TaskGraph:
    """
    DAG manager for execution ordering and parallel task discovery.
    """

    def __init__(self, steps: List[PlanStep]):
        self.nodes: Dict[int, TaskNode] = {step.id: TaskNode(step) for step in steps}
        self._build_graph()

    def _build_graph(self) -> None:
        """Links parent dependencies and child references."""
        for node in self.nodes.values():
            for dep_id in node.step.dependencies:
                if dep_id in self.nodes:
                    parent_node = self.nodes[dep_id]
                    node.parents.append(parent_node)
                    parent_node.children.append(node)

    def has_circular_dependency(self) -> bool:
        """Detects if graph contains circular dependency loops."""
        visited: Set[int] = set()
        rec_stack: Set[int] = set()

        def is_cyclic(node_id: int) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for child in self.nodes[node_id].children:
                if child.step_id not in visited:
                    if is_cyclic(child.step_id):
                        return True
                elif child.step_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if is_cyclic(node_id):
                    return True

        return False

    def get_executable_steps(self) -> List[PlanStep]:
        """
        Returns all pending steps whose dependencies are fully satisfied.
        Identifies independent steps that can be executed in parallel.
        """
        ready_steps: List[PlanStep] = []
        for node in self.nodes.values():
            if node.step.status == StepStatus.PENDING and node.is_ready():
                ready_steps.append(node.step)
        return ready_steps

    def get_topological_order(self) -> List[PlanStep]:
        """Returns steps ordered by dependency resolution sequence."""
        in_degree = {node_id: len(node.parents) for node_id, node in self.nodes.items()}
        queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
        order: List[PlanStep] = []

        while queue:
            curr_id = queue.pop(0)
            order.append(self.nodes[curr_id].step)

            for child in self.nodes[curr_id].children:
                in_degree[child.step_id] -= 1
                if in_degree[child.step_id] == 0:
                    queue.append(child.step_id)

        return order
