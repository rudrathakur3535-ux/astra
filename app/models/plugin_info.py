"""
Plugin Info Model for Project Astra.
Encapsulates plugin status, metadata, installation path, and configuration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import time
import uuid


class PluginStatus(str, Enum):
    DISCOVERED = "discovered"
    PERMISSIONS_PENDING = "permissions_pending"
    LOADED = "loaded"
    FAILED = "failed"
    UNLOADED = "unloaded"


@dataclass
class PluginInfo:
    """
    Represents an installed or discovered plugin in Astra OS.
    """
    name: str
    version: str
    author: str
    description: str
    entrypoint: str
    install_path: str
    permissions: List[str] = field(default_factory=list)
    status: PluginStatus = PluginStatus.DISCOVERED
    plugin_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "entrypoint": self.entrypoint,
            "install_path": self.install_path,
            "permissions": self.permissions,
            "status": self.status.value if isinstance(self.status, PluginStatus) else self.status,
            "config": self.config,
            "created_at": self.created_at
        }
