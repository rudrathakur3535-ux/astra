"""
Desktop Tools Package - Registration of desktop OS capabilities.
"""
from app.tools.tool_registry import tool_registry
from app.tools.desktop.app_launcher import LaunchAppTool
from app.tools.desktop.file_manager import CreateFolderTool, OpenFolderTool
from app.tools.desktop.window_manager import FocusWindowTool, ListWindowsTool
from app.tools.desktop.clipboard import ReadClipboardTool, WriteClipboardTool
from app.tools.desktop.system_info import GetSystemInfoTool

def register_desktop_tools() -> None:
    """Registers all desktop tools into global tool_registry."""
    tool_registry.register(LaunchAppTool())
    tool_registry.register(CreateFolderTool())
    tool_registry.register(OpenFolderTool())
    tool_registry.register(FocusWindowTool())
    tool_registry.register(ListWindowsTool())
    tool_registry.register(ReadClipboardTool())
    tool_registry.register(WriteClipboardTool())
    tool_registry.register(GetSystemInfoTool())

# Automatically register desktop tools on package import
register_desktop_tools()

__all__ = [
    "LaunchAppTool",
    "CreateFolderTool",
    "OpenFolderTool",
    "FocusWindowTool",
    "ListWindowsTool",
    "ReadClipboardTool",
    "WriteClipboardTool",
    "GetSystemInfoTool",
    "register_desktop_tools"
]
