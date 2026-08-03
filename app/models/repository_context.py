"""
Repository Context Model for Project Astra OS.
Represents GitHub repositories, branches, commits, PR diffs, and issue contexts.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time


@dataclass
class PullRequestDiff:
    pr_id: int
    title: str
    author: str
    branch: str
    changed_files: List[str]
    diff_text: str
    status: str = "open"
    created_at: float = field(default_factory=time.time)


@dataclass
class RepositoryContext:
    repo_name: str
    owner: str
    default_branch: str = "main"
    open_prs: List[PullRequestDiff] = field(default_factory=list)
    recent_commits: List[Dict[str, Any]] = field(default_factory=list)
    open_issues: List[Dict[str, Any]] = field(default_factory=list)
    fetched_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo_name": self.repo_name,
            "owner": self.owner,
            "default_branch": self.default_branch,
            "open_prs_count": len(self.open_prs),
            "recent_commits_count": len(self.recent_commits),
            "open_issues_count": len(self.open_issues),
            "fetched_at": self.fetched_at
        }
