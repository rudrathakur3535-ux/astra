from typing import Dict, Any
import pyperclip
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.utils.logger import logger

class ReadClipboardTool(BaseTool):
    """Tool to read current text contents from OS clipboard."""

    @property
    def name(self) -> str:
        return "read_clipboard"

    @property
    def description(self) -> str:
        return "Reads and returns text currently copied on the system clipboard."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    def execute(self) -> ToolResponse:
        try:
            content = pyperclip.paste()
            logger.info(f"Read clipboard content ({len(content)} chars)")
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data={"clipboard_text": content}
            )
        except Exception as e:
            logger.error(f"Failed to read clipboard: {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not read clipboard: {e}"
            )

class WriteClipboardTool(BaseTool):
    """Tool to copy text content onto system clipboard."""

    @property
    def name(self) -> str:
        return "write_clipboard"

    @property
    def description(self) -> str:
        return "Copies text content onto the system clipboard."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text string to copy onto the system clipboard."
                }
            },
            "required": ["text"]
        }

    def execute(self, text: str) -> ToolResponse:
        try:
            pyperclip.copy(text)
            logger.info(f"Wrote to clipboard ({len(text)} chars)")
            return ToolResponse(
                success=True,
                tool_name=self.name,
                data=f"Copied {len(text)} characters to clipboard."
            )
        except Exception as e:
            logger.error(f"Failed to write clipboard: {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not copy text to clipboard: {e}"
            )
