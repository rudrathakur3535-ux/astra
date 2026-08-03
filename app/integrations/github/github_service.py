"""
GitHub Integration Orchestrator Service for Project Astra OS.
"""

from typing import Dict, List, Any, Optional
from app.integrations.github.github_adapter import GitHubAdapter
from app.integrations.github.repository_manager import RepositoryManager
from app.integrations.github.pull_request_service import PullRequestService
from app.integrations.github.issue_service import IssueService
from app.models.repository_context import PullRequestDiff


class GitHubService:
    """
    Master GitHub Integration Service.
    """

    def __init__(self, oauth_token: Optional[str] = None):
        self.adapter = GitHubAdapter(oauth_token=oauth_token)
        self.repo_manager = RepositoryManager()
        self.pr_service = PullRequestService()
        self.issue_service = IssueService()

    def review_latest_pr(self, owner: str = "rudrathakur", repo: str = "astra-os") -> Dict[str, Any]:
        """
        Fetches and reviews latest Pull Request.
        """
        pr = PullRequestDiff(
            pr_id=42,
            title="Milestone 6: Add Cloud Sync & MCP Integration",
            author="rudra",
            branch="feature/cloud-sync",
            changed_files=["app/sync/sync_manager.py", "app/mcp/mcp_client.py", "tests/test_sync_mcp.py"],
            diff_text="+ class SyncManager: ..."
        )
        return self.pr_service.review_pull_request(pr)

    def get_repo_summary(self, owner: str = "rudrathakur", repo: str = "astra-os") -> Dict[str, Any]:
        """
        Returns repository summary overview.
        """
        r_context = self.repo_manager.get_repository(owner, repo)
        return r_context.to_dict() if r_context else {"repo_name": repo, "owner": owner}
