"""
Dependency Analyzer Module for Project Astra.
Analyzes module import relationships, class inheritance, and detects circular dependencies.
"""

from typing import List, Dict, Set, Tuple
import os

from app.models.symbol import Symbol, SymbolType
from app.models.dependency import DependencyEdge, DependencyType
from app.utils.logger import logger


class DependencyAnalyzer:
    """
    Analyzes code dependency structures and detects circular dependency cycles.
    """

    def analyze_dependencies(self, symbols: List[Symbol]) -> List[DependencyEdge]:
        """
        Extracts dependency edges from symbol lists.
        """
        edges: List[DependencyEdge] = []

        for sym in symbols:
            if sym.symbol_type == SymbolType.IMPORT:
                edges.append(DependencyEdge(
                    source=sym.filepath,
                    target=sym.name,
                    dep_type=DependencyType.IMPORT,
                    line_number=sym.line_number,
                    filepath=sym.filepath
                ))

        logger.debug(f"Analyzed {len(edges)} dependency edges.")
        return edges

    def detect_circular_dependencies(self, edges: List[DependencyEdge]) -> List[List[str]]:
        """
        Detects circular import cycles using depth-first graph traversal.

        Returns:
            List[List[str]]: List of detected circular dependency chains.
        """
        graph: Dict[str, Set[str]] = {}
        for edge in edges:
            if edge.source not in graph:
                graph[edge.source] = set()
            graph[edge.source].add(edge.target)

        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: List[str] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    idx = rec_stack.index(neighbor)
                    cycle_chain = rec_stack[idx:] + [neighbor]
                    cycles.append(cycle_chain)

            rec_stack.pop()

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node)

        if cycles:
            logger.warning(f"Detected {len(cycles)} circular dependency loops.")
        return cycles
