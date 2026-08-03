"""
Plugin Permission Model for Project Astra.
Represents individual capability permissions requested by plugins.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PluginPermission:
    """
    Capability permission requirement requested by a plugin.
    """
    name: str
    description: str
    is_granted: bool = False
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "is_granted": self.is_granted,
            "reason": self.reason
        }
