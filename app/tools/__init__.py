"""
Tools Module - Base tool contracts, registry, router, desktop, and browser tool implementations.
"""
from app.tools.base_tool import BaseTool
from app.tools.tool_registry import ToolRegistry, tool_registry
from app.tools.tool_router import ToolRouter, tool_router
import app.tools.desktop  # Registers desktop tools
import app.tools.browser  # Registers browser tools
import app.tools.vision   # Registers vision tools

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "tool_registry",
    "ToolRouter",
    "tool_router"
]
