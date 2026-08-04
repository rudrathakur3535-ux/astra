from typing import List, Optional
from app.ports.memory_port import BaseMemoryPort
from app.models.memory_record import MemoryRecord, MemoryType

class MemoryManager:
    def __init__(self, adapter: BaseMemoryPort):
        self.adapter = adapter

    async def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        metadata: Optional[dict] = None
    ) -> str:
        record = MemoryRecord(
            memory_type=memory_type,
            content=content,
            metadata=metadata or {}
        )
        return await self.adapter.store(record)

    async def recall_context(self, query: str, limit: int = 3) -> str:
        records = await self.adapter.query(query, limit=limit)
        if not records:
            return ""
        lines = [f"- {r.content}" for r in records]
        return "\n".join(lines)
