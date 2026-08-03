"""
Working Memory Module for Project Astra.
Manages short-term active conversation context in RAM. Cleared on session reset.
"""

from typing import List, Dict, Any, Optional
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory


class WorkingMemory:
    """
    RAM-based working memory buffer for active conversation turns.
    """

    def __init__(self, capacity: int = 15):
        self.capacity = capacity
        self._buffer: List[MemoryRecord] = []

    def add_turn(self, role: str, content: str, importance: int = 5) -> MemoryRecord:
        """
        Adds a conversation turn (user/assistant) to working memory.
        """
        record = MemoryRecord(
            content=f"{role.capitalize()}: {content}",
            memory_type=MemoryType.WORKING,
            category=MemoryCategory.TEMPORARY,
            importance=importance,
            metadata={"role": role}
        )
        self._buffer.append(record)
        if len(self._buffer) > self.capacity:
            self._buffer.pop(0)  # Maintain max rolling capacity window
        return record

    def get_context_turns(self) -> List[MemoryRecord]:
        """Returns all current working memory turns in chronological order."""
        return list(self._buffer)

    def get_formatted_dialogue(self) -> str:
        """Formats active turns into a prompt-ready dialogue string."""
        return "\n".join([rec.content for rec in self._buffer])

    def clear(self) -> None:
        """Clears working memory session."""
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
