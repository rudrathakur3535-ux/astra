"""
Semantic Memory Module for Project Astra.
Manages conceptual knowledge, user preferences, and fact vectors using MemoryPort.
"""

from typing import List, Optional
from app.ports.memory_port import MemoryPort
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory
from app.models.memory_query import MemoryQuery


class SemanticMemory:
    """
    Semantic Memory Manager for long-term vector facts and user knowledge.
    """

    def __init__(self, relational_port: MemoryPort, vector_port: MemoryPort):
        self.relational_port = relational_port
        self.vector_port = vector_port

    def store_fact(
        self,
        content: str,
        category: MemoryCategory = MemoryCategory.PERMANENT,
        importance: int = 7,
        tags: Optional[List[str]] = None
    ) -> MemoryRecord:
        """
        Stores a long-term fact record into both relational and vector stores.
        """
        record = MemoryRecord(
            content=content,
            memory_type=MemoryType.SEMANTIC,
            category=category,
            importance=importance,
            tags=tags or []
        )
        self.relational_port.save_record(record)
        self.vector_port.save_record(record)
        return record

    def recall_facts(
        self,
        query_text: str,
        top_k: int = 5,
        min_importance: int = 1,
        categories: Optional[List[MemoryCategory]] = None
    ) -> List[MemoryRecord]:
        """
        Searches semantic facts using vector similarity search.
        """
        query = MemoryQuery(
            query_text=query_text,
            top_k=top_k,
            min_importance=min_importance,
            categories=categories,
            memory_types=[MemoryType.SEMANTIC]
        )
        results = self.vector_port.search_semantic(query)
        if not results:
            # Fallback to relational keyword search if vector search returns no matches
            results = self.relational_port.search_semantic(query)
        return results
