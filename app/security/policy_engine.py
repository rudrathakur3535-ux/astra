from typing import Dict, Any, List
from app.ports.security_port import BaseSecurityPort
from app.models.security_event import SecurityEvent, RiskLevel

class PolicyEngine(BaseSecurityPort):
    def __init__(self):
        self._audit_log: List[SecurityEvent] = []

    async def validate_action(self, action_name: str, parameters: dict) -> RiskLevel:
        action_lower = action_name.lower()
        if any(keyword in action_lower for keyword in ["delete", "remove", "drop", "exec_shell", "format"]):
            return RiskLevel.CRITICAL
        elif any(keyword in action_lower for keyword in ["write", "modify", "update", "post"]):
            return RiskLevel.HIGH
        elif any(keyword in action_lower for keyword in ["read", "fetch", "search"]):
            return RiskLevel.LOW
        return RiskLevel.MEDIUM

    async def record_event(self, event: SecurityEvent) -> None:
        self._audit_log.append(event)
