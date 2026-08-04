from abc import ABC, abstractmethod
from app.models.security_event import SecurityEvent, RiskLevel

class BaseSecurityPort(ABC):
    @abstractmethod
    async def validate_action(self, action_name: str, parameters: dict) -> RiskLevel:
        pass

    @abstractmethod
    async def record_event(self, event: SecurityEvent) -> None:
        pass

# Alias for backwards compatibility across existing modules
SecurityPort = BaseSecurityPort
