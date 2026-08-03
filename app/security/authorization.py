"""
Authorization Engine for Project Astra OS.
Evaluates role-based access control (RBAC) and resource scope policies.
"""

from typing import List, Optional, Dict, Any
from app.models.user_identity import UserIdentity, UserRole
from app.models.permission import ActionType, ResourceScope, PermissionRule


class AuthorizationEngine:
    """
    Evaluates permission rules and user access policies.
    """

    def __init__(self):
        self._rules: List[PermissionRule] = []
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Sets default system permission rules."""
        self._rules.append(PermissionRule(
            rule_id="rule-admin-all",
            action=ActionType.ADMIN,
            resource_scope=ResourceScope("system", "*"),
            allowed_roles=["owner", "admin"],
            requires_confirmation=False
        ))
        self._rules.append(PermissionRule(
            rule_id="rule-delete-files",
            action=ActionType.DELETE,
            resource_scope=ResourceScope("file", "*"),
            allowed_roles=["owner", "admin"],
            requires_confirmation=True
        ))
        self._rules.append(PermissionRule(
            rule_id="rule-execute-terminal",
            action=ActionType.EXECUTE,
            resource_scope=ResourceScope("terminal", "*"),
            allowed_roles=["owner", "admin"],
            requires_confirmation=True
        ))

    def add_permission_rule(self, rule: PermissionRule) -> None:
        """Adds a new permission rule."""
        self._rules.append(rule)

    def is_authorized(
        self,
        user: UserIdentity,
        action: ActionType,
        resource_scope: ResourceScope
    ) -> bool:
        """
        Evaluates whether a user identity is authorized for an action on a resource scope.
        """
        if not user.is_active:
            return False

        user_role = user.role.value if hasattr(user.role, "value") else str(user.role)

        # Owner role has superuser override
        if user.role == UserRole.OWNER or user_role == "owner":
            return True

        # Check explicit user permissions wildcard matching
        action_str = action.value if hasattr(action, "value") else str(action)
        req_perm = f"{action_str}:{resource_scope.resource_type}"

        for perm in user.permissions:
            if perm == "*" or perm == req_perm or perm == f"{action_str}:*":
                return True

        # Evaluate rules matching action and scope
        for rule in self._rules:
            rule_action = rule.action.value if hasattr(rule.action, "value") else str(rule.action)
            if rule_action == action_str or rule_action == "admin":
                if rule.resource_scope.resource_type in (resource_scope.resource_type, "*"):
                    if user_role in rule.allowed_roles:
                        return True

        return False
