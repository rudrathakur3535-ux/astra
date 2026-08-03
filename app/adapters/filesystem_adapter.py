"""
Filesystem Adapter for Project Astra.
Implements ProjectPort for reading source code files and scanning repository directory structures.
"""

import os
import json
from typing import List, Optional, Dict, Any

from app.ports.project_port import ProjectPort
from app.models.repository import Repository
from app.utils.logger import logger


class FilesystemAdapter(ProjectPort):
    """
    Filesystem implementation of ProjectPort.
    """

    def __init__(self, index_dir: str = "app/database/code_index"):
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        self._cache: Dict[str, Repository] = {}

    def read_code_file(self, filepath: str) -> str:
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source code file not found: {filepath}")

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading source file '{filepath}': {e}")
            return ""

    def scan_python_files(self, root_dir: str) -> List[str]:
        root_dir = os.path.abspath(root_dir)
        if not os.path.exists(root_dir):
            return []

        py_files: List[str] = []
        ignored_dirs = {".git", ".pytest_cache", "__pycache__", "venv", "node_modules", "dist", "build", "chroma_db", "chroma_knowledge"}

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

        logger.info(f"Found {len(py_files)} Python files in '{root_dir}'.")
        return py_files

    def save_repository_index(self, repo: Repository) -> bool:
        self._cache[repo.name] = repo
        try:
            index_path = os.path.join(self.index_dir, f"{repo.name}.json")
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(repo.to_dict(), f, indent=2)
            logger.info(f"Saved repository index for '{repo.name}' to {index_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save repository index for '{repo.name}': {e}")
            return False

    def get_repository_index(self, repo_name: str) -> Optional[Repository]:
        return self._cache.get(repo_name)
