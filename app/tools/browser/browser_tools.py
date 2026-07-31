from typing import Dict, Any, Optional
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.browser.browser_manager import browser_manager
from app.utils.logger import logger

class OpenUrlTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.open_url"

    @property
    def description(self) -> str:
        return "Opens target web URL in active browser tab."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Web URL to open (e.g. 'https://github.com' or 'youtube.com')."}
            },
            "required": ["url"]
        }

    def execute(self, url: str) -> ToolResponse:
        res = browser_manager.adapter.open_url(url)
        return ToolResponse(success="error" not in res, tool_name=self.name, data=res, error_message=res.get("error"))

class GoogleSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.google_search"

    @property
    def description(self) -> str:
        return "Performs Google search query in browser."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query terms."}
            },
            "required": ["query"]
        }

    def execute(self, query: str) -> ToolResponse:
        res = browser_manager.adapter.google_search(query)
        return ToolResponse(success="error" not in res, tool_name=self.name, data=res, error_message=res.get("error"))

class YoutubeSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.youtube_search"

    @property
    def description(self) -> str:
        return "Searches YouTube for videos."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Video search query."}
            },
            "required": ["query"]
        }

    def execute(self, query: str) -> ToolResponse:
        res = browser_manager.adapter.youtube_search(query)
        return ToolResponse(success="error" not in res, tool_name=self.name, data=res, error_message=res.get("error"))

class GithubSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.github_search"

    @property
    def description(self) -> str:
        return "Searches GitHub for repositories or topics."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Repository or topic search query."}
            },
            "required": ["query"]
        }

    def execute(self, query: str) -> ToolResponse:
        res = browser_manager.adapter.github_search(query)
        return ToolResponse(success="error" not in res, tool_name=self.name, data=res, error_message=res.get("error"))

class CurrentPageTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.current_page"

    @property
    def description(self) -> str:
        return "Returns current page URL, title, and tab info."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self) -> ToolResponse:
        res = browser_manager.adapter.current_page()
        return ToolResponse(success=True, tool_name=self.name, data=res)

class PageTitleTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.page_title"

    @property
    def description(self) -> str:
        return "Returns title string of current active browser page."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self) -> ToolResponse:
        title = browser_manager.adapter.page_title()
        return ToolResponse(success=True, tool_name=self.name, data={"title": title})

class ReadPageTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.read_page"

    @property
    def description(self) -> str:
        return "Intelligent Reader: Extracts cleaned Markdown text from active webpage for reading or summarizing."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "max_length": {"type": "integer", "description": "Max text length to extract (default: 4000)."}
            }
        }

    def execute(self, max_length: int = 4000) -> ToolResponse:
        content = browser_manager.adapter.read_page(max_length=max_length)
        return ToolResponse(success=True, tool_name=self.name, data={"content": content})

class NewTabTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.new_tab"

    @property
    def description(self) -> str:
        return "Opens a new browser tab with optional target URL."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Optional URL to open in new tab."}
            }
        }

    def execute(self, url: Optional[str] = None) -> ToolResponse:
        res = browser_manager.adapter.new_tab(url=url)
        return ToolResponse(success=True, tool_name=self.name, data=res)

class CloseTabTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.close_tab"

    @property
    def description(self) -> str:
        return "Closes current active tab or specified tab index."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tab_index": {"type": "integer", "description": "Optional tab index to close."}
            }
        }

    def execute(self, tab_index: Optional[int] = None) -> ToolResponse:
        res = browser_manager.adapter.close_tab(tab_index=tab_index)
        return ToolResponse(success=True, tool_name=self.name, data=res)

class RefreshTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.refresh"

    @property
    def description(self) -> str:
        return "Refreshes active page."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self) -> ToolResponse:
        res = browser_manager.adapter.refresh()
        return ToolResponse(success=True, tool_name=self.name, data=res)

class BackTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.back"

    @property
    def description(self) -> str:
        return "Navigates back in browser history."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self) -> ToolResponse:
        res = browser_manager.adapter.back()
        return ToolResponse(success=True, tool_name=self.name, data=res)

class ForwardTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.forward"

    @property
    def description(self) -> str:
        return "Navigates forward in browser history."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self) -> ToolResponse:
        res = browser_manager.adapter.forward()
        return ToolResponse(success=True, tool_name=self.name, data=res)

class SwitchTabTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser.switch_tab"

    @property
    def description(self) -> str:
        return "Switches active page focus to target tab index."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tab_index": {"type": "integer", "description": "Tab index (0-based) to switch to."}
            },
            "required": ["tab_index"]
        }

    def execute(self, tab_index: int) -> ToolResponse:
        res = browser_manager.adapter.switch_tab(tab_index)
        return ToolResponse(success="error" not in res, tool_name=self.name, data=res, error_message=res.get("error"))
