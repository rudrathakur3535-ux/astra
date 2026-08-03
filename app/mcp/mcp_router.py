"""
MCP Tool Router for Project Astra OS.
Routes tool calls to the appropriate external or internal MCP server handlers.
"""

from typing import Dict, Any, Optional
from app.mcp.mcp_client import MCPClient
from app.mcp.mcp_registry import MCPRegistry


class MCPRouter:
    """
    Router for executing tool requests against MCP servers.
    """

    def __init__(self, registry: Optional[MCPRegistry] = None):
        self.registry = registry or MCPRegistry()
        self.client = self.registry.client

    def route_tool_call(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes a tool call to specified MCP server.
        """
        if not self.client.adapter.is_connected(server_name):
            # Attempt auto-connection
            self.client.connect_server(server_name)

        return self.client.execute_tool(server_name, tool_name, arguments)
