"""
Search Result Model for Project Astra.
Represents candidate chunks returned by Knowledge Engine retrieval and re-ranking.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from app.models.chunk import Chunk


@dataclass
class SearchResult:
    """
    Candidate chunk wrapper with similarity score, re-ranking score, and citation text.
    """
    chunk: Chunk
    similarity_score: float = 0.0
    rerank_score: float = 0.0
    citation_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "text": self.chunk.text,
            "document_name": self.chunk.document_name,
            "page_number": self.chunk.page_number,
            "section_heading": self.chunk.section_heading,
            "similarity_score": round(self.similarity_score, 4),
            "rerank_score": round(self.rerank_score, 4),
            "citation_text": self.citation_text
        }
