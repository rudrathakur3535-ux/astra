"""
Security Event Model for Project Astra OS.
Represents security alerts, policy violations, and threat events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class SecuritySeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """
    Security event alert log entry.
    """
    event_type: str
    message: str
    severity: SecuritySeverity = SecuritySeverity.WARNING
    event_id: str = field(default_factory=lambda: f"sec-{uuid.uuid4().hex[:8]}")
    user_id: Optional[str] = None
    subsystem: str = "security"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "severity": self.severity.value if isinstance(self.severity, SecuritySeverity) else self.severity,
            "user_id": self.user_id,
            "subsystem": self.subsystem,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
