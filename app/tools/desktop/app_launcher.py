import os
import subprocess
from typing import Dict, Any
from app.tools.base_tool import BaseTool
from app.models.tool_response import ToolResponse
from app.utils.logger import logger

class LaunchAppTool(BaseTool):
    """Tool to launch desktop applications like Chrome, VS Code, Notepad, Calculator, etc."""

    # Common app mappings for Windows
    APP_MAPPINGS = {
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "vs code": "code",
        "vscode": "code",
        "code": "code",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "spotify": "spotify.exe",
        "explorer": "explorer.exe",
        "terminal": "wt.exe",
        "cmd": "cmd.exe"
    }

    @property
    def name(self) -> str:
        return "launch_app"

    @property
    def description(self) -> str:
        return "Opens a specified desktop application (e.g. Chrome, VS Code, Notepad, Calculator)."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Name of the application to launch (e.g. 'chrome', 'vscode', 'notepad', 'calculator')."
                }
            },
            "required": ["app_name"]
        }

    def execute(self, app_name: str) -> ToolResponse:
        clean_name = app_name.strip().lower()
        executable = self.APP_MAPPINGS.get(clean_name, clean_name)

        try:
            logger.info(f"Launching application: '{clean_name}' (Executable: {executable})")
            
            # Windows execution launch
            if os.name == "nt":
                try:
                    os.startfile(executable)
                except Exception:
                    subprocess.Popen([executable], shell=True)
            else:
                subprocess.Popen([executable])

            return ToolResponse(
                success=True,
                tool_name=self.name,
                data=f"Successfully launched {app_name}."
            )

        except Exception as e:
            logger.error(f"Failed to launch application '{app_name}': {e}")
            return ToolResponse(
                success=False,
                tool_name=self.name,
                error_message=f"Failed to launch '{app_name}': {e}"
            )
