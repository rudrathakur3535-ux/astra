"""
Project Port Interface for Project Astra (Hexagonal Architecture).
Enforces decoupling between core codebase intelligence and filesystem / storage adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.symbol import Symbol
from app.models.repository import Repository


class ProjectPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Codebase Intelligence Adapters.
    """

    @abstractmethod
    def read_code_file(self, filepath: str) -> str:
        """Reads code file content safely."""
        pass

    @abstractmethod
    def scan_python_files(self, root_dir: str) -> List[str]:
        """Scans directory recursively for Python files."""
        pass

    @abstractmethod
    def save_repository_index(self, repo: Repository) -> bool:
        """Saves repository graph index."""
        pass

    @abstractmethod
    def get_repository_index(self, repo_name: str) -> Optional[Repository]:
        """Retrieves indexed repository graph."""
        pass
