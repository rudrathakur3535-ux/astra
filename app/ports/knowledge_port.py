"""
Knowledge Port Interface for Project Astra (Hexagonal Architecture).
Enforces strict decoupling between core RAG logic and vector store implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.document import Document
from app.models.chunk import Chunk


class KnowledgePort(ABC):
    """
    Abstract Hexagonal Port interface for Astra Knowledge Base Vector Adapters.
    """

    @abstractmethod
    def save_chunks(self, chunks: List[Chunk], collection: str = "project_docs") -> List[str]:
        """Indexes and saves a list of document chunks into the specified collection."""
        pass

    @abstractmethod
    def search_vector(
        self,
        query_vector: List[float],
        top_k: int = 10,
        collection: str = "project_docs",
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """Performs vector similarity search against the knowledge collection."""
        pass

    @abstractmethod
    def get_document_by_hash(self, file_hash: str, collection: str = "project_docs") -> Optional[Document]:
        """Checks if a document file hash is already indexed."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str, collection: str = "project_docs") -> bool:
        """Deletes all chunks belonging to a document from the vector store."""
        pass

    @abstractmethod
    def clear_collection(self, collection: str = "project_docs") -> bool:
        """Clears all vectors in a specified collection."""
        pass
