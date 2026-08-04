import sqlite3
import json
import asyncio
from typing import List, Optional
from app.ports.memory_port import BaseMemoryPort
from app.models.memory_record import MemoryRecord, MemoryType

class SQLiteMemoryAdapter(BaseMemoryPort):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        if db_path == ":memory:":
            self.db_path = "file:astramem?mode=memory&cache=shared"
            self._connection = sqlite3.connect(self.db_path, uri=True, check_same_thread=False)
        else:
            self._connection = None
        self._init_db()

    def _get_connection(self):
        if self._connection:
            return self._connection
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_records (
                record_id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                relevance_score REAL,
                created_at TEXT
            )
        ''')
        conn.commit()
        if not self._connection:
            conn.close()

    async def store(self, record: MemoryRecord) -> str:
        loop = asyncio.get_event_loop()
        def _execute():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memory_records 
                (record_id, memory_type, content, metadata, relevance_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                record.record_id,
                record.memory_type.value if hasattr(record.memory_type, 'value') else str(record.memory_type),
                record.content,
                json.dumps(record.metadata),
                record.relevance_score,
                record.created_at.isoformat()
            ))
            conn.commit()
            if not self._connection:
                conn.close()
            return record.record_id
        return await loop.run_in_executor(None, _execute)

    async def query(self, query_text: str, memory_type: Optional[MemoryType] = None, limit: int = 5) -> List[MemoryRecord]:
        loop = asyncio.get_event_loop()
        def _execute():
            records = []
            conn = self._get_connection()
            cursor = conn.cursor()
            mem_val = memory_type.value if hasattr(memory_type, 'value') else str(memory_type) if memory_type else None
            if mem_val:
                cursor.execute('''
                    SELECT record_id, memory_type, content, metadata, relevance_score, created_at 
                    FROM memory_records WHERE memory_type = ? ORDER BY created_at DESC LIMIT ?
                ''', (mem_val, limit))
            else:
                cursor.execute('''
                    SELECT record_id, memory_type, content, metadata, relevance_score, created_at 
                    FROM memory_records ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
            rows = cursor.fetchall()
            for row in rows:
                records.append(MemoryRecord(
                    record_id=row[0],
                    memory_type=MemoryType(row[1]),
                    content=row[2],
                    metadata=json.loads(row[3]) if row[3] else {},
                    relevance_score=row[4]
                ))
            if not self._connection:
                conn.close()
            return records
        return await loop.run_in_executor(None, _execute)

    async def clear_working_memory(self) -> bool:
        loop = asyncio.get_event_loop()
        def _execute():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory_records WHERE memory_type = ?", (MemoryType.WORKING.value,))
            conn.commit()
            if not self._connection:
                conn.close()
            return True
        return await loop.run_in_executor(None, _execute)
