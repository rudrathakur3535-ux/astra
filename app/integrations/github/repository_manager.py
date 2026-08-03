"""
Repository Manager for Project Astra OS.
Tracks repository tree structures, commit history, and branch states.
"""

from typing import Dict, List, Any, Optional
from app.models.repository_context import RepositoryContext


class RepositoryManager:
    """
    Manages repository index structures and recent commit tracking.
    """

    def __init__(self):
        self._repos: Dict[str, RepositoryContext] = {}
        self._init_mock_repo()

    def _init_mock_repo(self) -> None:
        mock = RepositoryContext(
            repo_name="astra-os",
            owner="rudrathakur",
            default_branch="master",
            recent_commits=[
                {"sha": "a32aef5", "message": "Day 5: Built Browser Subsystem", "author": "rudra"},
                {"sha": "8bc788e", "message": "Day 4: Desktop Control Engine", "author": "rudra"}
            ]
        )
        self._repos[f"{mock.owner}/{mock.repo_name}"] = mock

    def get_repository(self, owner: str, repo_name: str) -> Optional[RepositoryContext]:
        key = f"{owner}/{repo_name}"
        if key not in self._repos:
            # Create default context if missing
            self._repos[key] = RepositoryContext(repo_name=repo_name, owner=owner)
        return self._repos.get(key)
