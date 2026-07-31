from typing import Dict, Any, Optional
from app.browser.browser_manager import browser_manager

class PageController:
    """Controller handling high-level page interactions."""

    @staticmethod
    def navigate(url: str) -> Dict[str, Any]:
        return browser_manager.adapter.open_url(url)

    @staticmethod
    def get_summary(max_length: int = 4000) -> str:
        return browser_manager.adapter.read_page(max_length=max_length)
