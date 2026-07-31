from typing import Dict, Any, List, Optional
from app.utils.logger import logger

class BrowserSessionManager:
    """Session State Manager tracking open tabs, active tab index, and browsing history."""

    def __init__(self):
        self.active_tab_index: int = 0
        self.tabs_metadata: List[Dict[str, str]] = []
        self.history: List[Dict[str, str]] = []

    def update_tab_info(self, index: int, url: str, title: str) -> None:
        """Updates metadata for a specified tab index."""
        while len(self.tabs_metadata) <= index:
            self.tabs_metadata.append({"url": "about:blank", "title": "New Tab"})

        self.tabs_metadata[index] = {"url": url, "title": title}
        self.history.append({"url": url, "title": title, "tab_index": str(index)})
        logger.debug(f"Session updated tab {index}: {title} ({url})")

    def get_current_tab_info(self) -> Dict[str, Any]:
        """Returns metadata for current active tab."""
        if 0 <= self.active_tab_index < len(self.tabs_metadata):
            info = self.tabs_metadata[self.active_tab_index]
            return {
                "active_index": self.active_tab_index,
                "url": info["url"],
                "title": info["title"],
                "total_tabs": len(self.tabs_metadata)
            }
        return {
            "active_index": 0,
            "url": "about:blank",
            "title": "New Tab",
            "total_tabs": 1
        }

    def remove_tab_info(self, index: int) -> None:
        """Removes tab metadata when tab is closed."""
        if 0 <= index < len(self.tabs_metadata):
            self.tabs_metadata.pop(index)
            if self.active_tab_index >= len(self.tabs_metadata):
                self.active_tab_index = max(0, len(self.tabs_metadata) - 1)

    def find_tab_by_domain(self, domain: str) -> Optional[int]:
        """Context-aware lookup: finds open tab matching domain keyword (e.g. 'youtube')."""
        domain_clean = domain.strip().lower()
        for idx, tab in enumerate(self.tabs_metadata):
            if domain_clean in tab["url"].lower() or domain_clean in tab["title"].lower():
                return idx
        return None
