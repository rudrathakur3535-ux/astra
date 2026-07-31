"""
Browser Subsystem Package - Intelligent Browser Control, Session State, and Web Reader.
"""
from app.browser.browser_manager import BrowserManager, browser_manager
from app.browser.browser_session import BrowserSessionManager
from app.browser.web_reader import WebReader
from app.browser.navigation import NavigationHelper
from app.browser.downloads import DownloadManager
from app.browser.page_controller import PageController

__all__ = [
    "BrowserManager",
    "browser_manager",
    "BrowserSessionManager",
    "WebReader",
    "NavigationHelper",
    "DownloadManager",
    "PageController"
]
