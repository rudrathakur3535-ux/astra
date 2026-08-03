"""
Internal MCP Server for Project Astra OS.
Exposes Astra core tools, resources, and agents to external MCP callers.
"""

from typing import Dict, Any, List, Optional
from app.models.mcp_resource import MCPResource


class MCPServer:
    """
    Exposes Astra OS capabilities as a standard MCP Server.
    """

    def __init__(self, server_name: str = "astra-os-mcp"):
        self.server_name = server_name
        self._exposed_tools: Dict[str, Dict[str, Any]] = {}
        self._init_default_tools()

    def _init_default_tools(self) -> None:
        """Initializes default exposed Astra MCP tools."""
        self.register_tool(
            name="astra_code_analysis",
            description="Exposes Astra Code Intelligence AST analysis",
            handler=lambda args: {"result": f"Analyzed code target: {args.get('path')}"}
        )
        self.register_tool(
            name="astra_memory_query",
            description="Queries Astra hybrid vector/episodic memory",
            handler=lambda args: {"result": f"Queried memory for: {args.get('query')}"}
        )

    def register_tool(self, name: str, description: str, handler: Any) -> None:
        """Registers a tool on the internal MCP server."""
        self._exposed_tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }

    def list_exposed_tools(self) -> List[Dict[str, Any]]:
        """Lists tools exposed by Astra MCP server."""
        return [
            {"name": t["name"], "description": t["description"]} for t in self._exposed_tools.values()
        ]

    def handle_request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handles an incoming JSON-RPC MCP tool request."""
        tool = self._exposed_tools.get(tool_name)
        if not tool:
            return {"status": "error", "error": f"Tool '{tool_name}' not exposed on Astra MCP server."}

        try:
            res = tool["handler"](arguments)
            return {"status": "success", "data": res}
        except Exception as e:
            return {"status": "error", "error": str(e)}
