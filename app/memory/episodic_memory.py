"""
Episodic Memory Module for Project Astra.
Manages persistent experiential history and conversation events through MemoryPort.
"""

from typing import List, Optional
from app.ports.memory_port import MemoryPort
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory


class EpisodicMemory:
    """
    Episodic Memory Manager for persistent event history.
    """

    def __init__(self, port: MemoryPort):
        self.port = port

    def record_event(
        self,
        content: str,
        category: MemoryCategory = MemoryCategory.PERSONAL,
        importance: int = 5,
        tags: Optional[List[str]] = None
    ) -> MemoryRecord:
        """
        Stores an episodic event into persistent storage.
        """
        record = MemoryRecord(
            content=content,
            memory_type=MemoryType.EPISODIC,
            category=category,
            importance=importance,
            tags=tags or []
        )
        self.port.save_record(record)
        return record

    def get_recent_history(self, limit: int = 20, min_importance: int = 1) -> List[MemoryRecord]:
        """
        Retrieves recent episodic records.
        """
        return self.port.get_episodic_history(limit=limit, min_importance=min_importance)
