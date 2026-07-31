from typing import Dict, Any, List
import pygetwindow as gw
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.utils.logger import logger

class FocusWindowTool(BaseTool):
    """Tool to search for and focus an active application window by title."""

    @property
    def name(self) -> str:
        return "focus_window"

    @property
    def description(self) -> str:
        return "Brings an open desktop application window into focus (e.g. Chrome, VS Code, Spotify)."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "window_title": {
                    "type": "string",
                    "description": "Partial or full title of the window to bring to focus (e.g. 'Chrome', 'Visual Studio Code')."
                }
            },
            "required": ["window_title"]
        }

    def execute(self, window_title: str) -> ToolResponse:
        title_query = window_title.strip().lower()
        try:
            matching_windows = [w for w in gw.getAllWindows() if title_query in w.title.lower()]

            if not matching_windows:
                all_titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
                return ToolResponse(
                    success=False,
                    tool_name=self.name,
                    error_message=f"No window found matching '{window_title}'. Active windows: {all_titles[:5]}"
                )

            target_window = matching_windows[0]
            if target_window.isMinimized:
                target_window.restore()
            target_window.activate()

            logger.info(f"Focused window: '{target_window.title}'")
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data=f"Successfully focused window: '{target_window.title}'"
            )

        except Exception as e:
            logger.error(f"Failed to focus window '{window_title}': {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not focus window '{window_title}': {e}"
            )

class ListWindowsTool(BaseTool):
    """Tool to list all visible desktop windows."""

    @property
    def name(self) -> str:
        return "list_windows"

    @property
    def description(self) -> str:
        return "Lists titles of all open visible desktop application windows."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    def execute(self) -> ToolResponse:
        try:
            titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data={"windows": titles}
            )
        except Exception as e:
            logger.error(f"Failed to list windows: {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not list open windows: {e}"
            )
