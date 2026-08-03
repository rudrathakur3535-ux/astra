"""
Call Graph Builder Module for Project Astra.
Builds function and method invocation trees across codebase AST nodes.
"""

import ast
from typing import Dict, List, Set
from app.utils.logger import logger


class CallGraphVisitor(ast.NodeVisitor):
    """
    AST Visitor tracking function calls inside function bodies.
    """

    def __init__(self):
        self.current_caller: str = "<global>"
        self.call_graph: Dict[str, Set[str]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prev_caller = self.current_caller
        self.current_caller = node.name
        if self.current_caller not in self.call_graph:
            self.call_graph[self.current_caller] = set()
        self.generic_visit(node)
        self.current_caller = prev_caller

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        prev_caller = self.current_caller
        self.current_caller = node.name
        if self.current_caller not in self.call_graph:
            self.call_graph[self.current_caller] = set()
        self.generic_visit(node)
        self.current_caller = prev_caller

    def visit_Call(self, node: ast.Call) -> None:
        callee_name = self._get_callee_name(node.func)
        if callee_name and self.current_caller != "<global>":
            if self.current_caller not in self.call_graph:
                self.call_graph[self.current_caller] = set()
            self.call_graph[self.current_caller].add(callee_name)
        self.generic_visit(node)

    def _get_callee_name(self, func_node: ast.AST) -> Optional[str]:
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None


class CallGraphBuilder:
    """
    Constructs global function call graphs across project source files.
    """

    def build_call_graph(self, ast_trees: List[Tuple[str, ast.AST]]) -> Dict[str, List[str]]:
        """
        Builds caller-to-callees invocation mapping dictionary.
        """
        visitor = CallGraphVisitor()
        for filepath, tree in ast_trees:
            if tree:
                visitor.visit(tree)

        # Convert sets to lists
        result_graph = {caller: sorted(list(callees)) for caller, callees in visitor.call_graph.items()}
        logger.debug(f"Built call graph for {len(result_graph)} functions.")
        return result_graph
