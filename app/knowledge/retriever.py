"""
Hybrid Retriever Module for Project Astra.
Combines dense semantic vector similarity search with sparse keyword matching for Knowledge RAG retrieval.
"""

from typing import List, Optional, Dict, Any
from app.ports.knowledge_port import KnowledgePort
from app.models.chunk import Chunk
from app.models.search_result import SearchResult
from app.knowledge.embeddings import KnowledgeEmbeddingProvider
from app.utils.logger import logger


class HybridRetriever:
    """
    Hybrid semantic + keyword document retriever.
    """

    def __init__(self, port: KnowledgePort, embedding_provider: Optional[KnowledgeEmbeddingProvider] = None):
        self.port = port
        self.embedding_provider = embedding_provider or KnowledgeEmbeddingProvider()

    def retrieve_candidates(
        self,
        query: str,
        top_k: int = 20,
        collection: str = "project_docs",
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Retrieves top candidate chunks using hybrid semantic search.

        Returns:
            List[SearchResult]: Candidate chunks with vector similarity scores.
        """
        logger.info(f"Retrieving top {top_k} knowledge candidates for query: '{query}' in collection '{collection}'")

        query_vector = self.embedding_provider.embed_text(query)
        chunks = self.port.search_vector(
            query_vector=query_vector,
            top_k=top_k,
            collection=collection,
            where_filter=where_filter
        )

        results: List[SearchResult] = []
        query_terms = set(query.lower().split())

        for idx, chunk in enumerate(chunks):
            # Compute baseline similarity score (higher for top vector ranks)
            sim_score = 1.0 - (idx * 0.04)
            if sim_score < 0.1:
                sim_score = 0.1

            # BM25-style keyword bonus
            chunk_terms = set(chunk.text.lower().split())
            overlap = len(query_terms.intersection(chunk_terms))
            bm25_bonus = (overlap / len(query_terms)) * 0.3 if query_terms else 0.0

            results.append(SearchResult(
                chunk=chunk,
                similarity_score=sim_score + bm25_bonus
            ))

        logger.debug(f"Retrieved {len(results)} candidate search results.")
        return results
