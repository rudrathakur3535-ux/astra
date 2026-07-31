"""
Browser Tools Package - Registers all Playwright browser capabilities.
"""
from app.tools.tool_registry import tool_registry
from app.tools.browser.browser_tools import (
    OpenUrlTool,
    GoogleSearchTool,
    YoutubeSearchTool,
    GithubSearchTool,
    CurrentPageTool,
    PageTitleTool,
    ReadPageTool,
    NewTabTool,
    CloseTabTool,
    RefreshTool,
    BackTool,
    ForwardTool,
    SwitchTabTool
)

def register_browser_tools() -> None:
    """Registers all 13 browser tools into tool_registry."""
    tool_registry.register(OpenUrlTool())
    tool_registry.register(GoogleSearchTool())
    tool_registry.register(YoutubeSearchTool())
    tool_registry.register(GithubSearchTool())
    tool_registry.register(CurrentPageTool())
    tool_registry.register(PageTitleTool())
    tool_registry.register(ReadPageTool())
    tool_registry.register(NewTabTool())
    tool_registry.register(CloseTabTool())
    tool_registry.register(RefreshTool())
    tool_registry.register(BackTool())
    tool_registry.register(ForwardTool())
    tool_registry.register(SwitchTabTool())

# Automatically register browser tools on import
register_browser_tools()

__all__ = [
    "register_browser_tools",
    "OpenUrlTool",
    "GoogleSearchTool",
    "YoutubeSearchTool",
    "GithubSearchTool",
    "CurrentPageTool",
    "PageTitleTool",
    "ReadPageTool",
    "NewTabTool",
    "CloseTabTool",
    "RefreshTool",
    "BackTool",
    "ForwardTool",
    "SwitchTabTool"
]
