from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BrowserPort(ABC):
    """Hexagonal Port defining contract for browser automation adapters."""

    @abstractmethod
    def open_url(self, url: str) -> Dict[str, Any]:
        """Navigates current active tab to given URL."""
        pass

    @abstractmethod
    def google_search(self, query: str) -> Dict[str, Any]:
        """Performs search on Google."""
        pass

    @abstractmethod
    def youtube_search(self, query: str) -> Dict[str, Any]:
        """Performs search on YouTube."""
        pass

    @abstractmethod
    def github_search(self, query: str) -> Dict[str, Any]:
        """Performs search on GitHub."""
        pass

    @abstractmethod
    def current_page(self) -> Dict[str, Any]:
        """Returns details of current page (url, title, tab index)."""
        pass

    @abstractmethod
    def page_title(self) -> str:
        """Returns title of active page."""
        pass

    @abstractmethod
    def read_page(self, max_length: int = 4000) -> str:
        """Extracts cleaned Markdown text content from current DOM."""
        pass

    @abstractmethod
    def new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        """Opens a new browser tab."""
        pass

    @abstractmethod
    def close_tab(self, tab_index: Optional[int] = None) -> Dict[str, Any]:
        """Closes current or specified tab."""
        pass

    @abstractmethod
    def switch_tab(self, tab_index: int) -> Dict[str, Any]:
        """Switches active page focus to target tab index."""
        pass

    @abstractmethod
    def refresh(self) -> Dict[str, Any]:
        """Refreshes current page."""
        pass

    @abstractmethod
    def back(self) -> Dict[str, Any]:
        """Navigates back in browser history."""
        pass

    @abstractmethod
    def forward(self) -> Dict[str, Any]:
        """Navigates forward in browser history."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Shuts down browser instance."""
        pass
