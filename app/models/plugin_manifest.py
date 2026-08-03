"""
Plugin Manifest Model for Project Astra.
Schema model representing `manifest.json` or `plugin.json`.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class PluginManifest:
    """
    Plugin manifest schema payload parsed from plugin.json.
    """
    name: str
    version: str
    author: str
    description: str
    entrypoint: str
    permissions: List[str] = field(default_factory=list)
    declared_tools: List[str] = field(default_factory=list)
    declared_agents: List[str] = field(default_factory=list)
    min_astra_version: str = "0.1.0"
    config_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "entrypoint": self.entrypoint,
            "permissions": self.permissions,
            "declared_tools": self.declared_tools,
            "declared_agents": self.declared_agents,
            "min_astra_version": self.min_astra_version,
            "config_schema": self.config_schema
        }
