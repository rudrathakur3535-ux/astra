"""
Project Service Facade for Project Astra.
High-level service interface for codebase indexing, AST symbol queries, dependency analysis, and architecture reports.
"""

from typing import Dict, Any, List, Optional
from app.ports.project_port import ProjectPort
from app.adapters.filesystem_adapter import FilesystemAdapter
from app.code.repository_indexer import RepositoryIndexer
from app.code.code_search import CodeSearchEngine
from app.code.refactoring_engine import RefactoringEngine
from app.code.code_explainer import CodeExplainer
from app.models.repository import Repository
from app.utils.logger import logger


class ProjectService:
    """
    High-level facade interface for Astra's Coding Intelligence Engine.
    """

    def __init__(self, port: Optional[ProjectPort] = None):
        self.port = port or FilesystemAdapter()
        self.indexer = RepositoryIndexer(port=self.port)
        self.search_engine = CodeSearchEngine()
        self.refactoring_engine = RefactoringEngine()
        self.explainer = CodeExplainer()

    def index_project(self, root_dir: str) -> Repository:
        """Indexes a Python project codebase into AST symbol and graph structures."""
        return self.indexer.index_repository(root_dir)

    def search_codebase(self, repo_name: str, query: str) -> List[Dict[str, Any]]:
        """Searches symbols and code structures matching query string."""
        repo = self.port.get_repository_index(repo_name)
        if not repo:
            logger.warning(f"Repository index for '{repo_name}' not found.")
            return []

        symbols = self.search_engine.search_symbols(repo, query)
        return [s.to_dict() for s in symbols]

    def analyze_health(self, repo_name: str) -> Dict[str, Any]:
        """Analyzes codebase health and generates refactoring recommendations."""
        repo = self.port.get_repository_index(repo_name)
        if not repo:
            return {"error": f"Repository index for '{repo_name}' not found."}
        return self.refactoring_engine.analyze_repository_health(repo)

    def explain_code_symbol(self, repo_name: str, symbol_name: str) -> str:
        """Generates natural language explanation for a class or function symbol."""
        repo = self.port.get_repository_index(repo_name)
        if not repo:
            return f"Repository index for '{repo_name}' not found."
        return self.explainer.explain_symbol(repo, symbol_name)

    def generate_architecture_report(self, repo_name: str) -> str:
        """Generates architectural summary report for an indexed codebase."""
        repo = self.port.get_repository_index(repo_name)
        if not repo:
            return f"Repository index for '{repo_name}' not found."
        return self.explainer.generate_architecture_report(repo)
