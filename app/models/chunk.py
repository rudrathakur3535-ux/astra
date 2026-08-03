"""
Chunk Model for Project Astra.
Represents an atomic text segment extracted from a document with full metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import uuid


@dataclass
class Chunk:
    """
    Represents an atomic text segment extracted from a document.
    """
    text: str
    doc_id: str
    chunk_index: int
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_name: str = ""
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    file_hash: str = ""
    collection: str = "project_docs"
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "document_name": self.document_name,
            "page_number": self.page_number,
            "section_heading": self.section_heading,
            "tags": self.tags,
            "file_hash": self.file_hash,
            "collection": self.collection,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
