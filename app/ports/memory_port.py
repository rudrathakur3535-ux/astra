"""
Memory Port Interface for Project Astra (Hexagonal Architecture).
Enforces strict decoupling between core memory domain and database storage adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.memory_record import MemoryRecord
from app.models.memory_query import MemoryQuery


class MemoryPort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Memory Storage Adapters.
    """

    @abstractmethod
    def save_record(self, record: MemoryRecord) -> str:
        """Saves or updates a memory record. Returns record_id."""
        pass

    @abstractmethod
    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        """Retrieves a single memory record by ID."""
        pass

    @abstractmethod
    def search_semantic(self, query: MemoryQuery) -> List[MemoryRecord]:
        """Performs vector semantic similarity search for records matching query."""
        pass

    @abstractmethod
    def get_episodic_history(self, limit: int = 20, min_importance: int = 1) -> List[MemoryRecord]:
        """Retrieves recent chronological episodic memory records."""
        pass

    @abstractmethod
    def delete_record(self, record_id: str) -> bool:
        """Permanently deletes a memory record by ID."""
        pass

    @abstractmethod
    def archive_record(self, record_id: str) -> bool:
        """Marks a record as archived without deleting it."""
        pass

    @abstractmethod
    def recover_corrupted_db(self) -> bool:
        """Attempts to recover or re-initialize database in case of corruption."""
        pass
