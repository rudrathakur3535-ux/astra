"""
Knowledge Package for Project Astra.
RAG 2.0 Knowledge Engine featuring multi-format document loading, smart chunking, incremental hash indexing, hybrid retrieval, re-ranking, and inline source citation generation.
"""

from app.knowledge.knowledge_service import KnowledgeService
from app.knowledge.document_loader import DocumentLoader
from app.knowledge.chunker import SmartChunker
from app.knowledge.metadata import MetadataExtractor
from app.knowledge.embeddings import KnowledgeEmbeddingProvider
from app.knowledge.retriever import HybridRetriever
from app.knowledge.reranker import ChunkReRanker
from app.knowledge.citation import CitationEngine
from app.knowledge.index_manager import IndexManager

__all__ = [
    "KnowledgeService",
    "DocumentLoader",
    "SmartChunker",
    "MetadataExtractor",
    "KnowledgeEmbeddingProvider",
    "HybridRetriever",
    "ChunkReRanker",
    "CitationEngine",
    "IndexManager"
]
