"""
Tools Module - Base tool contracts, registry, router, and tool implementations.
"""
from app.tools.base_tool import BaseTool
from app.tools.tool_registry import ToolRegistry, tool_registry
from app.tools.tool_router import ToolRouter, tool_router
import app.tools.desktop  # Automatically registers desktop tools

__all__ = [
    "BaseTool",
    "ToolRegistry",
    "tool_registry",
    "ToolRouter",
    "tool_router"
]
