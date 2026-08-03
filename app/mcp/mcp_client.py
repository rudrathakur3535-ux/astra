"""
MCP Client for Project Astra OS.
Connects to external Model Context Protocol (MCP) servers (GitHub, Notion, Drive, Filesystem).
"""

from typing import Dict, Any, List, Optional
from app.adapters.mcp_adapter import MCPAdapter
from app.models.mcp_resource import MCPResource


class MCPClient:
    """
    Client for interacting with external MCP servers via standard JSON-RPC tools.
    """

    def __init__(self, adapter: Optional[MCPAdapter] = None):
        self.adapter = adapter or MCPAdapter()

    def connect_server(self, server_name: str, transport: str = "stdio", config: Optional[Dict[str, Any]] = None) -> bool:
        """Connects to an external MCP server."""
        return self.adapter.register_server(server_name, transport_type=transport, config=config)

    def discover_tools(self, server_name: str) -> List[MCPResource]:
        """Discovers available tools/resources on an MCP server."""
        return self.adapter.list_resources(server_name)

    def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a tool call against an MCP server."""
        return self.adapter.call_tool(server_name, tool_name, arguments)
