"""
Model Context Protocol (MCP) Resource & Tool Model for Project Astra OS.
Represents external tools, prompts, and resources exposed by MCP servers.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class MCPResource:
    """
    MCP Resource or Tool Definition.
    """
    resource_uri: str
    name: str
    description: str
    server_name: str
    schema: Dict[str, Any] = field(default_factory=dict)
    resource_type: str = "tool"  # tool, prompt, resource
    is_active: bool = True
    discovered_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_uri": self.resource_uri,
            "name": self.name,
            "description": self.description,
            "server_name": self.server_name,
            "resource_type": self.resource_type,
            "schema": self.schema,
            "is_active": self.is_active,
            "discovered_at": self.discovered_at
        }
