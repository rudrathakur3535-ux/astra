"""
Smart Chunker Module for Project Astra.
Splits document segments into overlapping text chunks while preserving sentence boundaries and section headings.
"""

import os
from typing import List, Tuple, Optional
from app.models.document import Document
from app.models.chunk import Chunk
from app.utils.logger import logger


class SmartChunker:
    """
    Recursive character and section-aware document chunker.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        doc: Document,
        raw_segments: List[Tuple[str, int, str]]
    ) -> List[Chunk]:
        """
        Chunks raw document segments into atomic `Chunk` objects.

        Args:
            doc: Document metadata object.
            raw_segments: List of (segment_text, page_number, section_heading).

        Returns:
            List[Chunk]: Formatted document chunks.
        """
        chunks: List[Chunk] = []
        global_index = 0

        for text, page_num, section_heading in raw_segments:
            sub_texts = self._split_text(text)
            for sub_text in sub_texts:
                if not sub_text.strip():
                    continue

                chunk = Chunk(
                    doc_id=doc.doc_id,
                    chunk_index=global_index,
                    text=sub_text.strip(),
                    document_name=os.path.basename(doc.filepath),
                    page_number=page_num,
                    section_heading=section_heading,
                    file_hash=doc.file_hash,
                    collection=doc.collection
                )
                chunks.append(chunk)
                global_index += 1

        logger.debug(f"Chunked document '{doc.title}' into {len(chunks)} chunks.")
        return chunks

    def _split_text(self, text: str) -> List[str]:
        """Splits long text recursively using windowing and paragraph boundaries."""
        if len(text) <= self.chunk_size:
            return [text]

        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_length = 0

        for p in paragraphs:
            p_len = len(p)
            if current_length + p_len <= self.chunk_size:
                current_chunk.append(p)
                current_length += p_len + 2
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                current_chunk = [p]
                current_length = p_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Further split any remaining oversized chunks
        final_chunks = []
        for chunk_str in chunks:
            if len(chunk_str) > self.chunk_size:
                # Sliding window split
                start = 0
                while start < len(chunk_str):
                    end = start + self.chunk_size
                    final_chunks.append(chunk_str[start:end])
                    start += self.chunk_size - self.chunk_overlap
            else:
                final_chunks.append(chunk_str)

        return final_chunks
