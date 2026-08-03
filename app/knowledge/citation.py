"""
Citation Engine Module for Project Astra.
Formats precise inline source citations for RAG response grounding.
"""

from typing import List
from app.models.search_result import SearchResult
from app.utils.logger import logger


class CitationEngine:
    """
    Generates inline citation strings and pre-formatted system prompt context blocks.
    """

    @staticmethod
    def format_citation(result: SearchResult) -> str:
        """
        Formats a single citation string.
        Example: [FastAPI.pdf, Page 14, Section: Authentication]
        """
        chunk = result.chunk
        parts = [chunk.document_name]

        if chunk.page_number and chunk.page_number > 0:
            parts.append(f"Page {chunk.page_number}")

        if chunk.section_heading:
            parts.append(f"Section: {chunk.section_heading}")

        citation = f"[{', '.join(parts)}]"
        result.citation_text = citation
        return citation

    @classmethod
    def build_prompt_context(cls, results: List[SearchResult]) -> str:
        """
        Assembles a pre-formatted RAG context block with inline citations for LLM prompt injection.
        """
        if not results:
            return ""

        context_blocks = []
        for idx, res in enumerate(results, 1):
            citation = cls.format_citation(res)
            block = f"--- Source {idx} {citation} ---\n{res.chunk.text}"
            context_blocks.append(block)

        formatted_output = "\n\n".join(context_blocks)
        logger.debug(f"Assembled RAG prompt context with {len(results)} source citations.")
        return formatted_output
