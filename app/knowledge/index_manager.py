"""
Index Manager Module for Project Astra.
Manages incremental document indexing using SHA256 file hash change detection.
"""

from typing import List, Tuple, Dict, Any, Optional
import os

from app.ports.knowledge_port import KnowledgePort
from app.knowledge.document_loader import DocumentLoader
from app.knowledge.chunker import SmartChunker
from app.knowledge.metadata import MetadataExtractor
from app.models.document import Document
from app.models.chunk import Chunk
from app.utils.logger import logger


class IndexManager:
    """
    Incremental indexing manager preventing redundant re-indexing of unchanged files.
    """

    def __init__(
        self,
        port: KnowledgePort,
        loader: Optional[DocumentLoader] = None,
        chunker: Optional[SmartChunker] = None
    ):
        self.port = port
        self.loader = loader or DocumentLoader()
        self.chunker = chunker or SmartChunker()
        self.metadata_extractor = MetadataExtractor()

    def index_document(self, filepath: str, collection: str = "project_docs") -> Tuple[bool, int]:
        """
        Indexes a document file incrementally.

        Returns:
            Tuple[bool, int]: (indexed_or_updated, number_of_chunks)
        """
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            logger.error(f"Cannot index non-existent file: '{filepath}'")
            return False, 0

        # Compute SHA256 hash of file
        file_hash = self.metadata_extractor.compute_file_hash(filepath)

        # 1. Incremental Check: Skip if file hash already indexed
        existing_doc = self.port.get_document_by_hash(file_hash, collection=collection)
        if existing_doc:
            logger.info(f"File '{os.path.basename(filepath)}' unchanged (Hash matched). Skipping index.")
            return False, 0

        # 2. Parse file into document & raw segments
        doc, raw_segments = self.loader.load_document(filepath)
        doc.file_hash = file_hash
        doc.collection = collection

        # 3. Chunk document
        chunks = self.chunker.chunk_document(doc, raw_segments)

        # 4. Save chunks into vector store
        saved_ids = self.port.save_chunks(chunks, collection=collection)
        logger.info(f"Successfully indexed document '{doc.title}' ({len(saved_ids)} chunks saved).")

        return True, len(saved_ids)

    def index_git_repository(self, repo_path: str, collection: str = "code_repos") -> Dict[str, Any]:
        """
        Indexes an entire Git repository directory incrementally.
        """
        repo_docs = self.loader.load_git_repository(repo_path)
        indexed_count = 0
        total_chunks = 0

        for doc, raw_segments in repo_docs:
            file_hash = self.metadata_extractor.compute_file_hash(doc.filepath)
            existing_doc = self.port.get_document_by_hash(file_hash, collection=collection)
            if existing_doc:
                continue

            doc.file_hash = file_hash
            doc.collection = collection
            chunks = self.chunker.chunk_document(doc, raw_segments)
            saved_ids = self.port.save_chunks(chunks, collection=collection)

            indexed_count += 1
            total_chunks += len(saved_ids)

        logger.info(f"Indexed repository '{os.path.basename(repo_path)}': {indexed_count} new/updated files, {total_chunks} total chunks.")
        return {
            "indexed_files": indexed_count,
            "total_chunks": total_chunks
        }
