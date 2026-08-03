"""
ChromaDB Vector Adapter for Project Astra.
Implements MemoryPort for semantic similarity search over stored memory records using vector embeddings.
"""

import os
from typing import List, Optional, Dict, Any

from app.ports.memory_port import MemoryPort
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory
from app.models.memory_query import MemoryQuery
from app.memory.embeddings import BaseEmbeddingProvider, SentenceTransformerEmbedding, FastHashEmbedding
from app.utils.logger import logger


class ChromaDBAdapter(MemoryPort):
    """
    ChromaDB implementation of MemoryPort for semantic vector search.
    """

    def __init__(
        self,
        persist_directory: str = "app/database/chroma_db",
        collection_name: str = "astra_semantic_memory",
        embedding_provider: Optional[BaseEmbeddingProvider] = None
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider or FastHashEmbedding()
        os.makedirs(self.persist_directory, exist_ok=True)
        self._init_chroma()

    def _init_chroma(self) -> None:
        """Initializes ChromaDB persistent client and collection."""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.debug(f"ChromaDB initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB ({e}). Operating in memory vector mode.")
            self.client = None
            self.collection = None

    def save_record(self, record: MemoryRecord) -> str:
        """Embeds record content and stores in ChromaDB vector collection."""
        if not self.collection:
            logger.warning("ChromaDB collection unavailable; skipping vector indexing.")
            return record.record_id

        try:
            embedding = record.vector_embedding
            if not embedding:
                embedding = self.embedding_provider.embed_text(record.content)
                record.vector_embedding = embedding

            metadata = {
                "memory_type": record.memory_type.value if isinstance(record.memory_type, MemoryType) else record.memory_type,
                "category": record.category.value if isinstance(record.category, MemoryCategory) else record.category,
                "importance": record.importance,
                "timestamp": record.timestamp,
                "archived": int(record.archived)
            }

            self.collection.upsert(
                ids=[record.record_id],
                documents=[record.content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            logger.debug(f"Indexed vector for record {record.record_id} in ChromaDB.")
            return record.record_id
        except Exception as e:
            logger.error(f"Failed to save record to ChromaDB: {e}")
            return record.record_id

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        if not self.collection:
            return None
        try:
            res = self.collection.get(ids=[record_id], include=["documents", "metadatas", "embeddings"])
            if res and res["ids"] and len(res["ids"]) > 0:
                doc = res["documents"][0]
                meta = res["metadatas"][0]
                emb = res["embeddings"][0] if res.get("embeddings") is not None else None

                return MemoryRecord(
                    record_id=record_id,
                    content=doc,
                    memory_type=MemoryType(meta.get("memory_type", "semantic")),
                    category=MemoryCategory(meta.get("category", "personal")),
                    importance=meta.get("importance", 5),
                    timestamp=meta.get("timestamp", 0.0),
                    vector_embedding=emb,
                    archived=bool(meta.get("archived", 0))
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching record {record_id} from ChromaDB: {e}")
            return None

    def search_semantic(self, query: MemoryQuery) -> List[MemoryRecord]:
        """Performs cosine vector similarity search over stored memories."""
        if not self.collection or not query.query_text:
            return []

        try:
            query_vec = self.embedding_provider.embed_text(query.query_text)
            
            # Construct metadata filters
            where_conditions = []
            where_conditions.append({"importance": {"$gte": query.min_importance}})
            if not query.include_archived:
                where_conditions.append({"archived": {"$eq": 0}})

            if query.categories:
                cat_vals = [c.value if isinstance(c, MemoryCategory) else c for c in query.categories]
                if len(cat_vals) == 1:
                    where_conditions.append({"category": {"$eq": cat_vals[0]}})
                elif len(cat_vals) > 1:
                    where_conditions.append({"category": {"$in": cat_vals}})

            if len(where_conditions) == 1:
                where_filter = where_conditions[0]
            elif len(where_conditions) > 1:
                where_filter = {"$and": where_conditions}
            else:
                where_filter = None

            results = self.collection.query(
                query_embeddings=[query_vec],
                n_results=query.top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )

            records: List[MemoryRecord] = []
            if results and results["ids"] and len(results["ids"][0]) > 0:
                ids = results["ids"][0]
                docs = results["documents"][0]
                metas = results["metadatas"][0]

                for rec_id, doc, meta in zip(ids, docs, metas):
                    records.append(MemoryRecord(
                        record_id=rec_id,
                        content=doc,
                        memory_type=MemoryType(meta.get("memory_type", "semantic")),
                        category=MemoryCategory(meta.get("category", "personal")),
                        importance=meta.get("importance", 5),
                        timestamp=meta.get("timestamp", 0.0),
                        archived=bool(meta.get("archived", 0))
                    ))
            return records
        except Exception as e:
            logger.error(f"Semantic vector search failed: {e}")
            return []

    def get_episodic_history(self, limit: int = 20, min_importance: int = 1) -> List[MemoryRecord]:
        """Vector DB delegating episodic history queries to relational adapter."""
        return []

    def delete_record(self, record_id: str) -> bool:
        if not self.collection:
            return False
        try:
            self.collection.delete(ids=[record_id])
            return True
        except Exception as e:
            logger.error(f"Failed to delete record {record_id} from ChromaDB: {e}")
            return False

    def archive_record(self, record_id: str) -> bool:
        rec = self.get_record(record_id)
        if rec:
            rec.archived = True
            self.save_record(rec)
            return True
        return False

    def recover_corrupted_db(self) -> bool:
        try:
            self._init_chroma()
            return True
        except Exception:
            return False
