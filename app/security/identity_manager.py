"""
Identity Manager for Project Astra OS.
Manages user profiles, role-based access assignments (RBAC), and identity resolution.
"""

from typing import Dict, List, Optional, Any
from app.models.user_identity import UserIdentity, UserRole


class IdentityManager:
    """
    User Identity & Role-Based Access Control (RBAC) Manager.
    """

    ROLE_PERMISSIONS: Dict[UserRole, List[str]] = {
        UserRole.OWNER: ["*"],
        UserRole.ADMIN: [
            "read:*", "write:*", "execute:*", "tools:*", "plugins:*", "security:manage"
        ],
        UserRole.STANDARD_USER: [
            "read:*", "write:workspace", "execute:standard_tools", "browser:*", "memory:*"
        ],
        UserRole.GUEST: [
            "read:public", "execute:read_only_tools"
        ]
    }

    def __init__(self):
        self._users: Dict[str, UserIdentity] = {}
        self._init_default_owner()

    def _init_default_owner(self) -> None:
        """Initializes default owner user identity for local OS execution."""
        owner = UserIdentity(
            user_id="usr-owner-001",
            username="astra_owner",
            role=UserRole.OWNER,
            email="owner@astra.local",
            permissions=self.ROLE_PERMISSIONS[UserRole.OWNER]
        )
        self._users[owner.user_id] = owner
        self._users[owner.username] = owner

    def create_user(
        self,
        username: str,
        role: UserRole = UserRole.STANDARD_USER,
        email: Optional[str] = None,
        custom_permissions: Optional[List[str]] = None
    ) -> UserIdentity:
        """
        Creates and registers a new UserIdentity.
        """
        if username in self._users:
            return self.get_user(username)

        permissions = list(self.ROLE_PERMISSIONS.get(role, []))
        if custom_permissions:
            permissions.extend(custom_permissions)

        user = UserIdentity(
            username=username,
            role=role,
            email=email,
            permissions=permissions
        )

        self._users[user.user_id] = user
        self._users[username] = user
        return user

    def get_user(self, user_id_or_name: str) -> Optional[UserIdentity]:
        """Retrieves a user profile by ID or username."""
        return self._users.get(user_id_or_name)

    def list_users() -> List[Dict[str, Any]]:
        """Lists all registered user profiles."""
        unique_users = {u.user_id: u for u in self._users.values()}
        return [u.to_dict() for u in unique_users.values()]

    def deactivate_user(self, user_id_or_name: str) -> bool:
        """Deactivates a user profile."""
        user = self.get_user(user_id_or_name)
        if user:
            user.is_active = False
            return True
        return False
