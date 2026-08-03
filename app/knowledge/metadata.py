"""
Metadata Extractor Module for Project Astra.
Calculates SHA256 file hashes, tag metadata, and section headers.
"""

import hashlib
import os
from typing import Dict, Any, List
from app.models.document import Document
from app.utils.logger import logger


class MetadataExtractor:
    """
    Metadata extractor computing SHA256 hashes and file attributes.
    """

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        """
        Calculates SHA256 hash of a file for incremental indexing change detection.
        """
        if not os.path.exists(filepath):
            return ""

        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute file hash for '{filepath}': {e}")
            return ""

    @staticmethod
    def extract_document_tags(filepath: str, content_snippet: str = "") -> List[str]:
        """
        Extracts categorization tags based on file extension and content keywords.
        """
        ext = os.path.splitext(filepath)[1].lower()
        tags = [ext.lstrip(".")]

        snippet_lower = content_snippet.lower()
        if "api" in snippet_lower or "endpoint" in snippet_lower:
            tags.append("api")
        if "auth" in snippet_lower or "oauth" in snippet_lower:
            tags.append("security")
        if "database" in snippet_lower or "sql" in snippet_lower:
            tags.append("database")
        if "architecture" in snippet_lower or "hexagonal" in snippet_lower:
            tags.append("architecture")

        return tags
