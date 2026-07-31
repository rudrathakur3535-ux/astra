import os
import subprocess
from pathlib import Path
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.utils.logger import logger

class CreateFolderTool(BaseTool):
    """Tool to create a new folder/directory on the filesystem."""

    @property
    def name(self) -> str:
        return "create_folder"

    @property
    def description(self) -> str:
        return "Creates a new folder at the specified directory path."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Name or relative/absolute path of the folder to create (e.g. 'AI' or 'C:/Users/Rudra/Desktop/AI')."
                }
            },
            "required": ["folder_name"]
        }

    def execute(self, folder_name: str) -> ToolResponse:
        try:
            target_path = Path(folder_name).expanduser().resolve()
            target_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {target_path}")

            return ToolResponse(
                success=True,
                tool_name=self.name,
                data=f"Created folder successfully at: '{target_path}'"
            )
        except Exception as e:
            logger.error(f"Failed to create folder '{folder_name}': {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not create folder '{folder_name}': {e}"
            )

class OpenFolderTool(BaseTool):
    """Tool to open a directory folder in Windows File Explorer or VS Code."""

    @property
    def name(self) -> str:
        return "open_folder"

    @property
    def description(self) -> str:
        return "Opens a directory folder in Windows File Explorer or VS Code."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "Path of the folder to open (e.g. 'Downloads', 'Documents', 'DSA')."
                },
                "open_in_vscode": {
                    "type": "boolean",
                    "description": "If true, opens the folder in VS Code instead of File Explorer."
                }
            },
            "required": ["folder_path"]
        }

    def execute(self, folder_path: str, open_in_vscode: bool = False) -> ToolResponse:
        try:
            # Common shortcuts resolution
            user_home = Path.home()
            path_str = folder_path.strip().lower()

            if path_str == "downloads":
                target_path = user_home / "Downloads"
            elif path_str in ("desktop", "dsa"):
                target_path = user_home / "Desktop"
            elif path_str == "documents":
                target_path = user_home / "Documents"
            else:
                target_path = Path(folder_path).expanduser().resolve()

            if not target_path.exists():
                return ToolResponse(
                    success=False,
                    tool_name=self.name,
                    error_message=f"Path '{target_path}' does not exist."
                )

            if open_in_vscode:
                logger.info(f"Opening folder in VS Code: {target_path}")
                subprocess.Popen(["code", str(target_path)], shell=True)
                return ToolResponse(
                    success=True,
                    tool_name=self.name,
                    data=f"Opened '{target_path}' in VS Code."
                )
            else:
                logger.info(f"Opening folder in File Explorer: {target_path}")
                if os.name == "nt":
                    os.startfile(str(target_path))
                else:
                    subprocess.Popen(["xdg-open", str(target_path)])
                return ToolResponse(
                    success=True,
                    tool_name=self.name,
                    data=f"Opened folder '{target_path}' in File Explorer."
                )

        except Exception as e:
            logger.error(f"Failed to open folder '{folder_path}': {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Could not open folder '{folder_path}': {e}"
            )
