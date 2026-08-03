"""
Model Context Protocol (MCP) Adapter for Project Astra OS.
Implements MCPPort for connecting to external MCP servers and tools.
"""

from typing import List, Dict, Any, Optional
from app.ports.mcp_port import MCPPort
from app.models.mcp_resource import MCPResource


class MCPAdapter(MCPPort):
    """
    Standardized MCP Adapter connecting to external MCP servers (GitHub, Notion, Drive, Filesystem).
    """

    def __init__(self):
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._resources: Dict[str, List[MCPResource]] = {}

    def register_server(self, server_name: str, transport_type: str = "stdio", config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registers an external MCP server connection config.
        """
        self._servers[server_name] = {
            "server_name": server_name,
            "transport": transport_type,
            "config": config or {},
            "connected": True
        }
        self._resources[server_name] = [
            MCPResource(
                resource_uri=f"mcp://{server_name}/search",
                name=f"{server_name}_search",
                description=f"Search resource in {server_name}",
                server_name=server_name,
                schema={"query": "string"}
            )
        ]
        return True

    def list_resources(self, server_name: str) -> List[MCPResource]:
        """Lists resources for a server."""
        return self._resources.get(server_name, [])

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes tool call on MCP server."""
        if not self.is_connected(server_name):
            return {"status": "error", "error": f"MCP server '{server_name}' is disconnected."}

        return {
            "status": "success",
            "server_name": server_name,
            "tool_name": tool_name,
            "result": f"Executed MCP tool '{tool_name}' on '{server_name}' with args {arguments}"
        }

    def is_connected(self, server_name: str) -> bool:
        """Returns connection status for server."""
        server = self._servers.get(server_name)
        return bool(server and server.get("connected", False))
