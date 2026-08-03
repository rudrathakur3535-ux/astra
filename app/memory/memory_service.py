"""
Memory Service Facade for Project Astra.
High-level service interface injected into LLM orchestration and chat services.
"""

from typing import Dict, Any, List, Optional
from app.memory.embeddings import BaseEmbeddingProvider, FastHashEmbedding
from app.memory.memory_manager import MemoryManager
from app.memory.retriever import MemoryRetriever
from app.models.memory_record import MemoryRecord, MemoryCategory
from app.utils.logger import logger


class MemoryService:
    """
    High-level facade interface for Astra's long-term memory operations.
    """

    def __init__(
        self,
        db_path: str = "app/database/astra_memory.db",
        chroma_dir: str = "app/database/chroma_db",
        embedding_provider: Optional[BaseEmbeddingProvider] = None
    ):
        from app.adapters.sqlite_adapter import SQLiteAdapter
        from app.adapters.chromadb_adapter import ChromaDBAdapter

        self.embedding_provider = embedding_provider or FastHashEmbedding()
        self.sqlite_adapter = SQLiteAdapter(db_path=db_path)
        self.chroma_adapter = ChromaDBAdapter(
            persist_directory=chroma_dir,
            embedding_provider=self.embedding_provider
        )

        self.manager = MemoryManager(
            relational_port=self.sqlite_adapter,
            vector_port=self.chroma_adapter
        )

        self.retriever = MemoryRetriever(
            working_memory=self.manager.working_memory,
            episodic_memory=self.manager.episodic_memory,
            semantic_memory=self.manager.semantic_memory
        )

    def record_user_turn(self, user_query: str, assistant_response: str, importance: int = 5) -> None:
        """Records an active conversation interaction."""
        self.manager.add_interaction(
            user_message=user_query,
            assistant_response=assistant_response,
            importance=importance
        )

    def remember_fact(
        self,
        fact: str,
        category: MemoryCategory = MemoryCategory.PERMANENT,
        importance: int = 7,
        tags: Optional[List[str]] = None
    ) -> MemoryRecord:
        """Stores an explicit user preference, goal, or project fact."""
        return self.manager.store_fact(
            fact=fact,
            category=category,
            importance=importance,
            tags=tags
        )

    def retrieve_memory_context(self, user_query: str, min_importance: int = 5) -> Dict[str, Any]:
        """Retrieves combined memory context before generating LLM response."""
        return self.retriever.retrieve_context_for_prompt(
            user_query=user_query,
            min_importance=min_importance
        )

    def run_reflection_cycle(self) -> Dict[str, Any]:
        """Triggers memory reflection, duplicate merging, and archiving."""
        return self.manager.run_reflection()
