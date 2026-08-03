"""
Notion Workspace Indexer for Project Astra OS.
Indexes Notion pages, documents, and database records.
"""

from typing import Dict, List, Any, Optional
import time


class NotionWorkspaceIndexer:
    """
    Indexes Notion workspace hierarchy and pages.
    """

    def __init__(self):
        self._indexed_pages: Dict[str, Dict[str, Any]] = {}
        self._init_mock_pages()

    def _init_mock_pages(self) -> None:
        self._indexed_pages["page-001"] = {
            "page_id": "page-001",
            "title": "Project Astra Architecture Roadmap",
            "content": "Milestone 7: Real Integrations & AI Workspace Platform.",
            "last_edited": time.time()
        }

    def index_page(self, page_id: str, title: str, content: str) -> Dict[str, Any]:
        entry = {
            "page_id": page_id,
            "title": title,
            "content": content,
            "last_edited": time.time()
        }
        self._indexed_pages[page_id] = entry
        return entry

    def search_pages(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        return [
            p for p in self._indexed_pages.values()
            if query_lower in p["title"].lower() or query_lower in p["content"].lower()
        ]
