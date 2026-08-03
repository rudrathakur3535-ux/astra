"""
Vision Tools Package - Registration of visual perception capabilities.
"""
from app.tools.tool_registry import tool_registry
from app.tools.vision.vision_tools import (
    CaptureScreenTool,
    AnalyzeScreenTool,
    CaptureRegionTool
)

def register_vision_tools() -> None:
    """Registers all vision tools into global tool_registry."""
    tool_registry.register(CaptureScreenTool())
    tool_registry.register(AnalyzeScreenTool())
    tool_registry.register(CaptureRegionTool())

# Automatically register vision tools on package import
register_vision_tools()

__all__ = [
    "CaptureScreenTool",
    "AnalyzeScreenTool",
    "CaptureRegionTool",
    "register_vision_tools"
]
