"""
ChromaDB Knowledge Adapter for Project Astra.
Implements KnowledgePort using ChromaDB with multi-collection isolation and metadata indexing.
"""

import os
from typing import List, Optional, Dict, Any

from app.ports.knowledge_port import KnowledgePort
from app.models.document import Document, DocumentType
from app.models.chunk import Chunk
from app.memory.embeddings import BaseEmbeddingProvider, FastHashEmbedding
from app.utils.logger import logger


class ChromaDBKnowledgeAdapter(KnowledgePort):
    """
    Multi-collection ChromaDB implementation of KnowledgePort.
    """

    def __init__(
        self,
        persist_directory: str = "app/database/chroma_knowledge",
        embedding_provider: Optional[BaseEmbeddingProvider] = None
    ):
        self.persist_directory = persist_directory
        self.embedding_provider = embedding_provider or FastHashEmbedding()
        os.makedirs(self.persist_directory, exist_ok=True)
        self._collections: Dict[str, Any] = {}
        self._init_chroma()

    def _init_chroma(self) -> None:
        """Initializes ChromaDB persistent client."""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.debug(f"ChromaDB Knowledge Adapter initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB Knowledge Adapter ({e}). Operating in memory fallback mode.")
            self.client = None

    def _get_collection(self, collection_name: str) -> Any:
        """Retrieves or creates a named ChromaDB vector collection."""
        if not self.client:
            return None

        if collection_name not in self._collections:
            try:
                col = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                self._collections[collection_name] = col
            except Exception as e:
                logger.error(f"Failed to get collection '{collection_name}': {e}")
                return None
        return self._collections.get(collection_name)

    def save_chunks(self, chunks: List[Chunk], collection: str = "project_docs") -> List[str]:
        col = self._get_collection(collection)
        if not col or not chunks:
            return []

        ids: List[str] = []
        documents: List[str] = []
        embeddings: List[List[float]] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            emb = chunk.embedding
            if not emb:
                emb = self.embedding_provider.embed_text(chunk.text)
                chunk.embedding = emb

            meta = {
                "doc_id": chunk.doc_id,
                "chunk_index": chunk.chunk_index,
                "document_name": chunk.document_name,
                "page_number": chunk.page_number if chunk.page_number is not None else -1,
                "section_heading": chunk.section_heading or "",
                "file_hash": chunk.file_hash,
                "created_at": chunk.created_at
            }

            ids.append(chunk.chunk_id)
            documents.append(chunk.text)
            embeddings.append(emb)
            metadatas.append(meta)

        try:
            col.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            logger.info(f"Indexed {len(chunks)} chunks into collection '{collection}'.")
            return ids
        except Exception as e:
            logger.error(f"Failed to upsert chunks into collection '{collection}': {e}")
            return []

    def search_vector(
        self,
        query_vector: List[float],
        top_k: int = 10,
        collection: str = "project_docs",
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        col = self._get_collection(collection)
        if not col:
            return []

        try:
            results = col.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            chunks: List[Chunk] = []
            if results and results["ids"] and len(results["ids"][0]) > 0:
                ids = results["ids"][0]
                docs = results["documents"][0]
                metas = results["metadatas"][0]

                for chunk_id, text, meta in zip(ids, docs, metas):
                    page_num = meta.get("page_number")
                    if page_num == -1:
                        page_num = None

                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        doc_id=meta.get("doc_id", ""),
                        chunk_index=meta.get("chunk_index", 0),
                        text=text,
                        document_name=meta.get("document_name", ""),
                        page_number=page_num,
                        section_heading=meta.get("section_heading") or None,
                        file_hash=meta.get("file_hash", ""),
                        collection=collection,
                        created_at=meta.get("created_at", 0.0)
                    ))

            return chunks
        except Exception as e:
            logger.error(f"Vector search failed in collection '{collection}': {e}")
            return []

    def get_document_by_hash(self, file_hash: str, collection: str = "project_docs") -> Optional[Document]:
        col = self._get_collection(collection)
        if not col or not file_hash:
            return None

        try:
            results = col.get(where={"file_hash": file_hash}, limit=1)
            if results and results["ids"] and len(results["ids"]) > 0:
                meta = results["metadatas"][0]
                return Document(
                    doc_id=meta.get("doc_id", ""),
                    filepath=meta.get("document_name", ""),
                    file_hash=file_hash,
                    collection=collection
                )
            return None
        except Exception as e:
            logger.error(f"Error checking document by hash: {e}")
            return None

    def delete_document(self, doc_id: str, collection: str = "project_docs") -> bool:
        col = self._get_collection(collection)
        if not col:
            return False

        try:
            col.delete(where={"doc_id": doc_id})
            logger.info(f"Deleted document '{doc_id}' from collection '{collection}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document '{doc_id}': {e}")
            return False

    def clear_collection(self, collection: str = "project_docs") -> bool:
        if not self.client:
            return False
        try:
            self.client.delete_collection(name=collection)
            if collection in self._collections:
                del self._collections[collection]
            logger.info(f"Cleared vector collection '{collection}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection '{collection}': {e}")
            return False
