"""
Unit tests for Day 6 Long-Term Memory System (The Brain That Never Forgets).
Tests Hexagonal MemoryPort adapters, working memory, episodic memory, semantic vector search,
summarization, corrupted DB recovery, duplicate handling, and reflection.
"""

import os
import sqlite3
import pytest
from typing import List

from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory
from app.models.memory_query import MemoryQuery
from app.adapters.sqlite_adapter import SQLiteAdapter
from app.adapters.chromadb_adapter import ChromaDBAdapter
from app.memory.embeddings import FastHashEmbedding
from app.memory.working_memory import WorkingMemory
from app.memory.episodic_memory import EpisodicMemory
from app.memory.semantic_memory import SemanticMemory
from app.memory.summarizer import ContextSummarizer
from app.memory.memory_manager import MemoryManager
from app.memory.memory_service import MemoryService


@pytest.fixture
def tmp_sqlite(tmp_path):
    db_file = str(tmp_path / "test_memory.db")
    adapter = SQLiteAdapter(db_path=db_file)
    return adapter


@pytest.fixture
def tmp_chroma(tmp_path):
    chroma_dir = str(tmp_path / "chroma_db")
    adapter = ChromaDBAdapter(
        persist_directory=chroma_dir,
        collection_name="test_collection",
        embedding_provider=FastHashEmbedding()
    )
    return adapter


class TestSQLiteAdapter:
    def test_empty_database_query(self, tmp_sqlite):
        history = tmp_sqlite.get_episodic_history(limit=10)
        assert history == []
        rec = tmp_sqlite.get_record("nonexistent_id")
        assert rec is None

    def test_record_insertion_and_retrieval(self, tmp_sqlite):
        record = MemoryRecord(
            content="Rudra prefers VS Code for Python development.",
            memory_type=MemoryType.SEMANTIC,
            category=MemoryCategory.CODING,
            importance=9
        )
        rec_id = tmp_sqlite.save_record(record)
        assert rec_id == record.record_id

        retrieved = tmp_sqlite.get_record(rec_id)
        assert retrieved is not None
        assert retrieved.content == record.content
        assert retrieved.category == MemoryCategory.CODING
        assert retrieved.importance == 9

    def test_corrupted_database_recovery(self, tmp_path):
        import gc
        db_file = str(tmp_path / "corrupt_test.db")
        adapter = SQLiteAdapter(db_path=db_file)
        del adapter
        gc.collect()

        # Corrupt the file
        with open(db_file, "wb") as f:
            f.write(b"NOT A VALID SQLITE FILE CORRUPTED HEADER DATA")

        # Attempt recovery with fresh adapter instance
        recovery_adapter = SQLiteAdapter(db_path=db_file)
        rec = MemoryRecord(content="Post corruption test memory")
        saved_id = recovery_adapter.save_record(rec)
        assert recovery_adapter.get_record(saved_id) is not None


class TestSemanticVectorSearch:
    def test_semantic_retrieval(self, tmp_sqlite, tmp_chroma):
        semantic = SemanticMemory(relational_port=tmp_sqlite, vector_port=tmp_chroma)
        semantic.store_fact(
            content="Rudra is building an AI OS named Project Astra.",
            category=MemoryCategory.PROJECTS,
            importance=10
        )
        semantic.store_fact(
            content="The user bought groceries at the supermarket yesterday.",
            category=MemoryCategory.PERSONAL,
            importance=3
        )

        results = semantic.recall_facts(query_text="Project Astra AI OS", top_k=2, min_importance=5)
        assert len(results) >= 1
        assert "Astra" in results[0].content


class TestWorkingMemory:
    def test_working_memory_turn_buffering(self):
        wm = WorkingMemory(capacity=3)
        wm.add_turn("user", "Hello")
        wm.add_turn("assistant", "Hi Rudra!")
        wm.add_turn("user", "What is my goal?")
        wm.add_turn("assistant", "To build Astra OS.")

        assert len(wm) == 3
        turns = wm.get_context_turns()
        assert turns[0].content == "Assistant: Hi Rudra!"
        assert turns[-1].content == "Assistant: To build Astra OS."


class TestSummarizer:
    def test_summarize_records(self):
        summarizer = ContextSummarizer(max_token_threshold=10)
        records = [
            MemoryRecord(content="Turn 1: Discussing architecture and design patterns in detail for Astra OS", importance=5),
            MemoryRecord(content="Turn 2: Implementing Hexagonal MemoryPort contract with SQLite and ChromaDB adapters", importance=8),
        ]
        assert summarizer.should_summarize(records) is True
        summary = summarizer.summarize_records(records)
        assert summary.importance == 8
        assert "Conversation Summary" in summary.content


class TestMemoryManagerAndReflection:
    def test_reflection_and_duplicate_merging(self, tmp_sqlite, tmp_chroma):
        manager = MemoryManager(relational_port=tmp_sqlite, vector_port=tmp_chroma)

        # Store duplicate facts
        manager.store_fact("Rudra loves clean Hexagonal Architecture.", importance=8)
        manager.store_fact("Rudra loves clean Hexagonal Architecture.", importance=8)

        stats = manager.run_reflection()
        assert stats["merged_count"] >= 1


class TestMemoryServiceFacade:
    def test_memory_service_full_flow(self, tmp_path):
        service = MemoryService(
            db_path=str(tmp_path / "service_mem.db"),
            chroma_dir=str(tmp_path / "service_chroma")
        )

        service.remember_fact(
            fact="Rudra's dream is to become a Principal AI Systems Engineer.",
            category=MemoryCategory.CAREER,
            importance=10
        )

        service.record_user_turn(
            user_query="What is my primary career goal?",
            assistant_response="Your goal is to become a Principal AI Systems Engineer."
        )

        context = service.retrieve_memory_context(user_query="AI Engineer career", min_importance=5)
        assert "formatted_context_block" in context
        assert len(context["working_turns"]) == 2
