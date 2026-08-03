"""
Policy Engine & Guardrail Evaluator for Project Astra OS.
Evaluates security policies, confirmation requirements, and audit trail enforcement for OS operations.
"""

from typing import Dict, Any, Optional, Callable
from app.models.user_identity import UserIdentity
from app.models.permission import ActionType, ResourceScope
from app.security.authorization import AuthorizationEngine
from app.security.audit_logger import AuditLogger


class PolicyEngine:
    """
    Dynamic Policy Engine enforcing authorization, user confirmation prompts, and immutable audit logs.
    """

    HIGH_RISK_OPERATIONS = {
        "delete_file": ActionType.DELETE,
        "delete_folder": ActionType.DELETE,
        "kill_process": ActionType.EXECUTE,
        "run_terminal_command": ActionType.EXECUTE,
        "modify_system_config": ActionType.WRITE
    }

    def __init__(
        self,
        authorization_engine: Optional[AuthorizationEngine] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        self.auth_engine = authorization_engine or AuthorizationEngine()
        self.audit_logger = audit_logger or AuditLogger()
        self._prompt_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None

    def set_prompt_callback(self, callback: Callable[[str, Dict[str, Any]], bool]) -> None:
        """Registers the UI prompt callback for user confirmation."""
        self._prompt_callback = callback

    def evaluate_action(
        self,
        user: UserIdentity,
        action_name: str,
        resource: str,
        parameters: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> bool:
        """
        Evaluates whether an action is allowed based on user role, policy confirmation, and audit logs.
        """
        params = parameters or {}

        # Map action_name to ActionType and ResourceScope
        action_type = self.HIGH_RISK_OPERATIONS.get(action_name, ActionType.EXECUTE)
        resource_scope = ResourceScope(resource_type="tool", resource_id=action_name)

        # 1. Authorization check
        authorized = self.auth_engine.is_authorized(user, action_type, resource_scope)
        if not authorized:
            self.audit_logger.log_action(
                user_id=user.user_id,
                action=action_name,
                tool_name=action_name,
                resource=resource,
                result="REJECTED_UNAUTHORIZED",
                workflow_id=workflow_id,
                parameters=params
            )
            return False

        # 2. High-Risk User Confirmation Prompt check
        if action_name in self.HIGH_RISK_OPERATIONS:
            if self._prompt_callback:
                user_approved = self._prompt_callback(action_name, params)
                if not user_approved:
                    self.audit_logger.log_action(
                        user_id=user.user_id,
                        action=action_name,
                        tool_name=action_name,
                        resource=resource,
                        result="REJECTED_USER_DENIED",
                        workflow_id=workflow_id,
                        parameters=params
                    )
                    return False

        # 3. Log successful policy evaluation
        self.audit_logger.log_action(
            user_id=user.user_id,
            action=action_name,
            tool_name=action_name,
            resource=resource,
            result="APPROVED",
            workflow_id=workflow_id,
            parameters=params
        )
        return True
