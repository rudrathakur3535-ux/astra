"""
Audit Record Model for Project Astra OS.
Represents immutable security audit trail entries.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid
import hashlib
import json


@dataclass
class AuditRecord:
    """
    Immutable Security Audit Record.
    """
    user_id: str
    action: str
    tool_name: str
    resource: str
    result: str
    workflow_id: Optional[str] = None
    audit_id: str = field(default_factory=lambda: f"aud-{uuid.uuid4().hex[:10]}")
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    signature: str = ""

    def __post_init__(self):
        if not self.signature:
            self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generates a SHA-256 hash signature for tamper detection."""
        payload = f"{self.audit_id}:{self.user_id}:{self.action}:{self.tool_name}:{self.resource}:{self.result}:{self.timestamp}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "workflow_id": self.workflow_id,
            "action": self.action,
            "tool_name": self.tool_name,
            "resource": self.resource,
            "result": self.result,
            "parameters": self.parameters,
            "signature": self.signature
        }
