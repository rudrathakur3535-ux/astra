"""
Code Package for Project Astra.
Coding Intelligence Engine featuring AST parsing, symbol extraction, dependency graph generation, call graph tracking, code search, refactoring suggestions, and architectural explainer.
"""

from app.code.project_service import ProjectService
from app.code.ast_parser import ASTParser
from app.code.symbol_extractor import SymbolExtractor
from app.code.dependency_analyzer import DependencyAnalyzer
from app.code.call_graph import CallGraphBuilder
from app.code.repository_indexer import RepositoryIndexer
from app.code.code_search import CodeSearchEngine
from app.code.refactoring_engine import RefactoringEngine
from app.code.code_explainer import CodeExplainer

__all__ = [
    "ProjectService",
    "ASTParser",
    "SymbolExtractor",
    "DependencyAnalyzer",
    "CallGraphBuilder",
    "RepositoryIndexer",
    "CodeSearchEngine",
    "RefactoringEngine",
    "CodeExplainer"
]
