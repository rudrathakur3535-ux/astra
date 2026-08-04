from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.memory_record import MemoryRecord, MemoryType

class BaseMemoryPort(ABC):
    @abstractmethod
    async def store(self, record: MemoryRecord) -> str:
        pass

    @abstractmethod
    async def query(self, query_text: str, memory_type: Optional[MemoryType] = None, limit: int = 5) -> List[MemoryRecord]:
        pass

    @abstractmethod
    async def clear_working_memory(self) -> bool:
        pass

# Alias for backwards compatibility
MemoryPort = BaseMemoryPort
