"""
Notion Integration Service for Project Astra OS.
Reads pages, creates notes, and updates Notion database entries.
"""

from typing import Dict, List, Any, Optional
from app.integrations.notion.workspace_indexer import NotionWorkspaceIndexer


class NotionService:
    """
    Notion API Service orchestrator.
    """

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token
        self.indexer = NotionWorkspaceIndexer()

    def search_workspace(self, query: str) -> List[Dict[str, Any]]:
        """Searches Notion workspace pages."""
        return self.indexer.search_pages(query)

    def create_page(self, title: str, content: str) -> Dict[str, Any]:
        """Creates a new Notion page entry."""
        page_id = f"notion-{hash(title) % 10000}"
        return self.indexer.index_page(page_id, title, content)
