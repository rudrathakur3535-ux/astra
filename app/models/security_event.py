from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(BaseModel):
    event_id: str
    action: str
    risk_level: RiskLevel
    user_confirmed: bool = False
    context_details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

SecuritySeverity = RiskLevel

