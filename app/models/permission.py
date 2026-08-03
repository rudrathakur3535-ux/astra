"""
Permission Models for Project Astra OS.
Defines action types, resource scopes, and authorization rules.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time


class ActionType(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class ResourceScope:
    """
    Scope definition for protected resources (e.g., file system, browser, tools).
    """
    resource_type: str
    resource_id: str = "*"

    def __str__(self) -> str:
        return f"{self.resource_type}:{self.resource_id}"


@dataclass
class PermissionRule:
    """
    Authorization permission rule.
    """
    rule_id: str
    action: ActionType
    resource_scope: ResourceScope
    allowed_roles: list = field(default_factory=lambda: ["owner", "admin"])
    requires_confirmation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "action": self.action.value if isinstance(self.action, ActionType) else self.action,
            "resource_scope": str(self.resource_scope),
            "allowed_roles": self.allowed_roles,
            "requires_confirmation": self.requires_confirmation
        }
