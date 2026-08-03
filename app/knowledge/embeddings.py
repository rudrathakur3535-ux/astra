"""
Knowledge Embedding Provider Module for Project Astra.
Provides dense vector embedding generation for Knowledge Engine document chunks.
"""

from typing import List, Optional
from app.memory.embeddings import BaseEmbeddingProvider, SentenceTransformerEmbedding, FastHashEmbedding
from app.utils.logger import logger


class KnowledgeEmbeddingProvider:
    """
    Vector embedding provider wrapper for Knowledge Engine.
    """

    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None):
        self.provider = provider or FastHashEmbedding()

    def embed_text(self, text: str) -> List[float]:
        return self.provider.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_batch(texts)
