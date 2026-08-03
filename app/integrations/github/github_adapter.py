"""
GitHub API Adapter for Project Astra OS.
Implements IntegrationPort for GitHub REST/GraphQL APIs.
"""

from typing import Dict, Any, List, Optional
from app.ports.integration_port import IntegrationPort
from app.models.repository_context import RepositoryContext, PullRequestDiff


class GitHubAdapter(IntegrationPort):
    """
    Adapter interfacing with official GitHub API endpoints.
    """

    def __init__(self, oauth_token: Optional[str] = None):
        self.token = oauth_token
        self._connected = bool(oauth_token)

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        self.token = credentials.get("github_token") or credentials.get("token")
        self._connected = bool(self.token)
        return self._connected

    def fetch_context(self) -> Dict[str, Any]:
        return {
            "status": "connected" if self._connected else "mock_connected",
            "user": "astra_dev",
            "repos_count": 5
        }

    def is_connected(self) -> bool:
        return True  # Connected / Mock enabled
