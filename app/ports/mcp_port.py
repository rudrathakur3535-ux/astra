"""
MCP Port Interface for Project Astra OS (Hexagonal Architecture).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.mcp_resource import MCPResource


class MCPPort(ABC):
    """
    Abstract Hexagonal Port interface for Model Context Protocol Adapters.
    """

    @abstractmethod
    def list_resources(self, server_name: str) -> List[MCPResource]:
        """Lists resources exposed by an MCP server."""
        pass

    @abstractmethod
    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a tool call on an MCP server."""
        pass

    @abstractmethod
    def is_connected(self, server_name: str) -> bool:
        """Returns connection status for an MCP server."""
        pass
