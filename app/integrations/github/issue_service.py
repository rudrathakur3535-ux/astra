"""
GitHub Issue Service for Project Astra OS.
Reads, tags, and summarizes repository issues.
"""

from typing import Dict, List, Any, Optional


class IssueService:
    """
    GitHub Issue Reader & Summarizer.
    """

    def summarize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarizes list of open issues.
        """
        if not issues:
            return {"summary": "No open issues found.", "critical_count": 0}

        critical = [i for i in issues if "bug" in str(i.get("labels", [])).lower() or "critical" in str(i.get("title", "")).lower()]

        return {
            "summary": f"Found {len(issues)} open issues ({len(critical)} critical/bug reports).",
            "total": len(issues),
            "critical_count": len(critical),
            "issues_list": issues
        }
