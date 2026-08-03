"""
User Identity Model for Project Astra OS.
Represents user profiles, roles, and identity definitions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
import time
import uuid


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    STANDARD_USER = "standard_user"
    GUEST = "guest"


@dataclass
class UserIdentity:
    """
    User Identity profile definition.
    """
    username: str
    role: UserRole = UserRole.STANDARD_USER
    user_id: str = field(default_factory=lambda: f"usr-{uuid.uuid4().hex[:8]}")
    email: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "email": self.email,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
