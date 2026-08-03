"""
MCP Registry for Project Astra OS.
Manages discovered external MCP servers, resources, and tool definitions.
"""

from typing import Dict, List, Optional, Any
from app.models.mcp_resource import MCPResource
from app.mcp.mcp_client import MCPClient


class MCPRegistry:
    """
    Registry for managing external MCP server connections and tools.
    """

    DEFAULT_SERVERS = ["github", "notion", "filesystem", "database", "google_drive"]

    def __init__(self, client: Optional[MCPClient] = None):
        self.client = client or MCPClient()
        self._registered_resources: Dict[str, MCPResource] = {}
        self._init_default_mcp_servers()

    def _init_default_mcp_servers(self) -> None:
        """Connects and discovers default MCP servers."""
        for s_name in self.DEFAULT_SERVERS:
            self.client.connect_server(s_name)
            tools = self.client.discover_tools(s_name)
            for tool in tools:
                self._registered_resources[tool.resource_uri] = tool

    def register_resource(self, resource: MCPResource) -> None:
        """Registers a discovered MCP resource."""
        self._registered_resources[resource.resource_uri] = resource

    def list_all_resources(self) -> List[Dict[str, Any]]:
        """Lists all registered MCP resources across servers."""
        return [r.to_dict() for r in self._registered_resources.values()]

    def get_resource(self, resource_uri: str) -> Optional[MCPResource]:
        """Retrieves a resource by URI."""
        return self._registered_resources.get(resource_uri)
