"""
SQLite Storage Adapter for Project Astra.
Implements MemoryPort for relational persistence of episodic and semantic memory records.
Provides automatic database corruption recovery.
"""

import json
import os
import sqlite3
import time
from typing import List, Optional, Dict, Any

from app.ports.memory_port import MemoryPort
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory
from app.models.memory_query import MemoryQuery
from app.utils.logger import logger


class SQLiteAdapter(MemoryPort):
    """
    SQLite implementation of MemoryPort.
    """

    def __init__(self, db_path: str = "app/database/astra_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a connection to the SQLite database with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes database schema."""
        conn = None
        should_recover = False
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    record_id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 5,
                    tags TEXT,
                    metadata TEXT,
                    timestamp REAL NOT NULL,
                    archived INTEGER NOT NULL DEFAULT 0
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_records(memory_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memory_records(category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_records(importance);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_records(timestamp);")
            conn.commit()
            logger.debug(f"SQLite DB initialized at {self.db_path}")
        except sqlite3.DatabaseError as e:
            logger.error(f"SQLite DB initialization error: {e}. Initiating corruption recovery.")
            should_recover = True
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        if should_recover:
            self.recover_corrupted_db()

    def save_record(self, record: MemoryRecord) -> str:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO memory_records 
                    (record_id, content, memory_type, category, importance, tags, metadata, timestamp, archived)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.record_id,
                    record.content,
                    record.memory_type.value if isinstance(record.memory_type, MemoryType) else record.memory_type,
                    record.category.value if isinstance(record.category, MemoryCategory) else record.category,
                    record.importance,
                    json.dumps(record.tags),
                    json.dumps(record.metadata),
                    record.timestamp,
                    1 if record.archived else 0
                ))
                conn.commit()
            logger.debug(f"Saved memory record {record.record_id} to SQLite.")
            return record.record_id
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error saving record {record.record_id}: {e}")
            self.recover_corrupted_db()
            raise RuntimeError(f"SQLite save failed: {e}") from e

    def get_record(self, record_id: str) -> Optional[MemoryRecord]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM memory_records WHERE record_id = ?", (record_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return self._row_to_record(row)
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error getting record {record_id}: {e}")
            return None

    def search_semantic(self, query: MemoryQuery) -> List[MemoryRecord]:
        """
        Fallback relational keyword/category search for SQLite adapter.
        Vector semantic search is primarily handled by ChromaDBAdapter.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT * FROM memory_records WHERE importance >= ? AND archived = ?"
                params: List[Any] = [query.min_importance, 1 if query.include_archived else 0]

                if query.categories:
                    cat_vals = [c.value if isinstance(c, MemoryCategory) else c for c in query.categories]
                    placeholders = ",".join(["?"] * len(cat_vals))
                    sql += f" AND category IN ({placeholders})"
                    params.extend(cat_vals)

                if query.memory_types:
                    type_vals = [t.value if isinstance(t, MemoryType) else t for t in query.memory_types]
                    placeholders = ",".join(["?"] * len(type_vals))
                    sql += f" AND memory_type IN ({placeholders})"
                    params.extend(type_vals)

                if query.query_text:
                    tokens = [t for t in query.query_text.split() if len(t) > 2]
                    if tokens:
                        token_clauses = " OR ".join(["content LIKE ?"] * len(tokens))
                        sql += f" AND ({token_clauses})"
                        for tok in tokens:
                            params.append(f"%{tok}%")

                sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
                params.append(query.top_k)

                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return [self._row_to_record(row) for row in rows]
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error searching records: {e}")
            return []

    def get_episodic_history(self, limit: int = 20, min_importance: int = 1) -> List[MemoryRecord]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM memory_records 
                    WHERE memory_type = ? AND importance >= ? AND archived = 0
                    ORDER BY timestamp DESC LIMIT ?
                """, (MemoryType.EPISODIC.value, min_importance, limit))
                rows = cursor.fetchall()
                records = [self._row_to_record(row) for row in rows]
                records.reverse()  # Return in chronological order
                return records
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error retrieving episodic history: {e}")
            return []

    def delete_record(self, record_id: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memory_records WHERE record_id = ?", (record_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.DatabaseError as e:
            logger.error(f"Error deleting record {record_id}: {e}")
            return False

    def archive_record(self, record_id: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE memory_records SET archived = 1 WHERE record_id = ?", (record_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.DatabaseError as e:
            logger.error(f"Error archiving record {record_id}: {e}")
            return False

    def recover_corrupted_db(self) -> bool:
        """
        Recovers from database corruption by creating a backup and re-initializing.
        """
        logger.warning(f"Attempting database recovery for {self.db_path}...")
        try:
            if os.path.exists(self.db_path):
                backup_path = f"{self.db_path}.corrupt_{int(time.time())}.bak"
                try:
                    os.rename(self.db_path, backup_path)
                except Exception:
                    os.remove(self.db_path)
                logger.info(f"Handled corrupted database backup for {self.db_path}")

            self._init_db()
            logger.info("Database successfully re-initialized after corruption recovery.")
            return True
        except Exception as e:
            logger.critical(f"Database recovery failed: {e}", exc_info=True)
            return False

    def _row_to_record(self, row: sqlite3.Row) -> MemoryRecord:
        """Helper to map SQLite row to MemoryRecord object."""
        return MemoryRecord(
            record_id=row["record_id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            category=MemoryCategory(row["category"]),
            importance=row["importance"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            timestamp=row["timestamp"],
            archived=bool(row["archived"])
        )
