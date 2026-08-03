"""
Chunk Re-Ranker Module for Project Astra.
Re-scores and filters top candidate chunks to extract the top-N most precise contexts for LLM prompts.
"""

from typing import List
from app.models.search_result import SearchResult
from app.utils.logger import logger


class ChunkReRanker:
    """
    Re-ranking engine scoring query-candidate relevance.
    """

    def rerank(self, query: str, candidates: List[SearchResult], top_n: int = 5) -> List[SearchResult]:
        """
        Re-scores top candidate chunks down to top_n best matches.
        """
        if not candidates:
            return []

        query_lower = query.lower()
        query_words = set(w for w in query_lower.split() if len(w) > 2)

        for result in candidates:
            chunk = result.chunk
            text_lower = chunk.text.lower()
            section_lower = (chunk.section_heading or "").lower()

            # Base score from vector + keyword retrieval
            score = result.similarity_score

            # 1. Exact phrase match bonus
            if query_lower in text_lower:
                score += 0.4

            # 2. Section heading match bonus
            if any(word in section_lower for word in query_words):
                score += 0.3

            # 3. Query term coverage ratio
            matched_words = sum(1 for word in query_words if word in text_lower)
            coverage = (matched_words / len(query_words)) if query_words else 0.0
            score += coverage * 0.3

            result.rerank_score = score

        # Sort candidates by rerank_score descending
        sorted_results = sorted(candidates, key=lambda r: r.rerank_score, reverse=True)
        top_results = sorted_results[:top_n]

        logger.info(f"Re-ranked {len(candidates)} candidates down to top {len(top_results)} results.")
        return top_results
