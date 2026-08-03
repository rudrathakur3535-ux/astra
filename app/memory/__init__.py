"""
Memory Package for Project Astra.
Hexagonal architecture long-term memory system with working, episodic, and semantic memory layers.
"""

from app.memory.embeddings import BaseEmbeddingProvider, SentenceTransformerEmbedding, FastHashEmbedding
from app.memory.working_memory import WorkingMemory
from app.memory.episodic_memory import EpisodicMemory
from app.memory.semantic_memory import SemanticMemory
from app.memory.summarizer import ContextSummarizer
from app.memory.retriever import MemoryRetriever
from app.memory.memory_manager import MemoryManager
from app.memory.memory_service import MemoryService

__all__ = [
    "BaseEmbeddingProvider",
    "SentenceTransformerEmbedding",
    "FastHashEmbedding",
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ContextSummarizer",
    "MemoryRetriever",
    "MemoryManager",
    "MemoryService"
]
