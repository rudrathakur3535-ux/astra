"""
Document Model for Project Astra.
Encapsulates raw document metadata, file hash, type, and source path.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import time
import uuid


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"
    TXT = "txt"
    HTML = "html"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass
class Document:
    """
    Represents an ingested document file in Astra's Knowledge Engine.
    """
    filepath: str
    doc_type: DocumentType = DocumentType.TXT
    title: str = ""
    file_hash: str = ""
    doc_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_size_bytes: int = 0
    collection: str = "project_docs"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "filepath": self.filepath,
            "title": self.title,
            "doc_type": self.doc_type.value if isinstance(self.doc_type, DocumentType) else self.doc_type,
            "file_hash": self.file_hash,
            "file_size_bytes": self.file_size_bytes,
            "collection": self.collection,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
