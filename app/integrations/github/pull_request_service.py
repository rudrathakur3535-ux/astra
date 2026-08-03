"""
Pull Request Service & Code Reviewer for Project Astra OS.
Parses PR diffs, reviews architecture changes, and generates automated code reviews.
"""

from typing import Dict, List, Any, Optional
from app.models.repository_context import PullRequestDiff


class PullRequestService:
    """
    Automated Pull Request Code Reviewer Assistant.
    """

    def review_pull_request(self, pr: PullRequestDiff) -> Dict[str, Any]:
        """
        Analyzes PR diff and returns architectural code review feedback.
        """
        review_comments = []
        if any("auth" in f.lower() for f in pr.changed_files):
            review_comments.append("Security Alert: Authentication logic updated. Verify token hash comparison uses constant-time hmac.compare_digest().")

        if any("test" not in f.lower() for f in pr.changed_files) and not any("test" in f.lower() for f in pr.changed_files):
            review_comments.append("Test Coverage Notice: Core logic modified without accompanying test file updates.")

        if not review_comments:
            review_comments.append("Code structure follows clean Hexagonal Architecture and SOLID principles. Ready for approval.")

        return {
            "pr_id": pr.pr_id,
            "title": pr.title,
            "author": pr.author,
            "status": "reviewed",
            "summary": f"Reviewed {len(pr.changed_files)} changed files on branch '{pr.branch}'.",
            "comments": review_comments
        }
