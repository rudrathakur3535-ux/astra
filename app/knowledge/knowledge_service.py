"""
Knowledge Service Facade for Project Astra.
High-level service interface for document ingestion, RAG search, re-ranking, and citation generation.
"""

from typing import Dict, Any, List, Optional, Tuple
from app.adapters.chromadb_knowledge_adapter import ChromaDBKnowledgeAdapter
from app.knowledge.index_manager import IndexManager
from app.knowledge.retriever import HybridRetriever
from app.knowledge.reranker import ChunkReRanker
from app.knowledge.citation import CitationEngine
from app.models.search_result import SearchResult
from app.utils.logger import logger


class KnowledgeService:
    """
    High-level facade interface for Astra's RAG 2.0 Knowledge Engine.
    """

    def __init__(
        self,
        persist_dir: str = "app/database/chroma_knowledge",
        adapter: Optional[ChromaDBKnowledgeAdapter] = None
    ):
        self.adapter = adapter or ChromaDBKnowledgeAdapter(persist_directory=persist_dir)
        self.index_manager = IndexManager(port=self.adapter)
        self.retriever = HybridRetriever(port=self.adapter)
        self.reranker = ChunkReRanker()
        self.citation_engine = CitationEngine()

    def ingest_document(self, filepath: str, collection: str = "project_docs") -> Tuple[bool, int]:
        """Ingests and indexes a single document incrementally."""
        return self.index_manager.index_document(filepath=filepath, collection=collection)

    def index_repository(self, repo_path: str, collection: str = "code_repos") -> Dict[str, Any]:
        """Indexes a full Git repository directory incrementally."""
        return self.index_manager.index_git_repository(repo_path=repo_path, collection=collection)

    def query_knowledge(
        self,
        query: str,
        top_k_candidates: int = 15,
        top_n_rerank: int = 5,
        collection: str = "project_docs"
    ) -> Dict[str, Any]:
        """
        Queries knowledge base, retrieves candidate chunks, re-ranks them, and builds pre-formatted context with inline citations.

        Returns:
            Dict containing:
                - 'results': List of top SearchResult objects
                - 'formatted_rag_context': Pre-formatted prompt text block with inline citations
                - 'total_retrieved': int
        """
        # 1. Hybrid Retrieval
        candidates = self.retriever.retrieve_candidates(
            query=query,
            top_k=top_k_candidates,
            collection=collection
        )

        # 2. Re-Ranking
        top_results = self.reranker.rerank(
            query=query,
            candidates=candidates,
            top_n=top_n_rerank
        )

        # 3. Citation Generation & Context Assembly
        rag_context = self.citation_engine.build_prompt_context(top_results)

        logger.info(f"[KnowledgeService] Query '{query}' returned {len(top_results)} re-ranked results.")
        return {
            "results": [r.to_dict() for r in top_results],
            "formatted_rag_context": rag_context,
            "total_retrieved": len(top_results)
        }
