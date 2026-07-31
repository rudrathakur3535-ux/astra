from typing import Dict, List, Optional, Any
from app.tools.base_tool import BaseTool
from app.utils.logger import logger

class ToolRegistry:
    """Central registry for discovering, inspecting, and managing Astra tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a tool instance into the global registry.
        
        Args:
            tool: Subclass instance of BaseTool.
        """
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool registration for '{tool.name}'.")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: '{tool.name}'")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Retrieves a registered tool instance by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Returns a list of all registered tool names."""
        return list(self._tools.keys())

    def get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        """Generates OpenAI function calling schemas for all registered tools."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

# Global default tool registry singleton
tool_registry = ToolRegistry()
