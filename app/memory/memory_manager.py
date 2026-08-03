"""
Memory Manager Module for Project Astra.
Coordinates multi-layer memory operations and executes autonomous Reflection cycles.
"""

from typing import List, Dict, Any, Optional
import time

from app.ports.memory_port import MemoryPort
from app.models.memory_record import MemoryRecord, MemoryType, MemoryCategory
from app.models.memory_query import MemoryQuery
from app.memory.working_memory import WorkingMemory
from app.memory.episodic_memory import EpisodicMemory
from app.memory.semantic_memory import SemanticMemory
from app.memory.summarizer import ContextSummarizer
from app.utils.logger import logger


class MemoryManager:
    """
    Central Coordinator & Reflection Engine for Astra's Long-Term Memory System.
    """

    def __init__(
        self,
        relational_port: MemoryPort,
        vector_port: MemoryPort,
        working_capacity: int = 15
    ):
        self.relational_port = relational_port
        self.vector_port = vector_port
        self.working_memory = WorkingMemory(capacity=working_capacity)
        self.episodic_memory = EpisodicMemory(port=relational_port)
        self.semantic_memory = SemanticMemory(relational_port=relational_port, vector_port=vector_port)
        self.summarizer = ContextSummarizer()

    def add_interaction(
        self,
        user_message: str,
        assistant_response: str,
        importance: int = 5,
        category: MemoryCategory = MemoryCategory.PERSONAL
    ) -> None:
        """
        Records a completed user-assistant interaction turn across working and episodic memory.
        """
        self.working_memory.add_turn("user", user_message, importance=importance)
        self.working_memory.add_turn("assistant", assistant_response, importance=importance)

        # Store episodic record
        event_str = f"User asked: '{user_message}' -> Astra responded: '{assistant_response}'"
        self.episodic_memory.record_event(
            content=event_str,
            category=category,
            importance=importance
        )

        # Auto-summarize working memory if token limit exceeded
        working_records = self.working_memory.get_context_turns()
        if self.summarizer.should_summarize(working_records):
            summary = self.summarizer.summarize_records(working_records)
            self.relational_port.save_record(summary)
            self.vector_port.save_record(summary)

    def store_fact(
        self,
        fact: str,
        category: MemoryCategory = MemoryCategory.PERMANENT,
        importance: int = 7,
        tags: Optional[List[str]] = None
    ) -> MemoryRecord:
        """
        Stores a specific user preference or long-term semantic fact.
        """
        return self.semantic_memory.store_fact(
            content=fact,
            category=category,
            importance=importance,
            tags=tags
        )

    def run_reflection(self) -> Dict[str, Any]:
        """
        Executes Reflection algorithm:
        1. Identifies recent episodic memories.
        2. Archives low-importance temporary items older than 24 hours.
        3. Merges duplicate memory entries.
        4. Synthesizes memory stats.
        """
        logger.info("Executing Memory Reflection Cycle...")
        now = time.time()
        archived_count = 0
        merged_count = 0

        # Query items to review
        query = MemoryQuery(min_importance=1, top_k=100)
        recent_records = self.relational_port.search_semantic(query)

        seen_contents = set()
        for rec in recent_records:
            # 1. Archive temporary items with low importance (<3) older than 1 hour
            if rec.category == MemoryCategory.TEMPORARY and rec.importance < 3:
                if (now - rec.timestamp) > 3600:
                    self.relational_port.archive_record(rec.record_id)
                    self.vector_port.archive_record(rec.record_id)
                    archived_count += 1
                    continue

            # 2. Identify exact duplicate contents
            clean_content = rec.content.strip().lower()
            if clean_content in seen_contents:
                self.relational_port.delete_record(rec.record_id)
                self.vector_port.delete_record(rec.record_id)
                merged_count += 1
            else:
                seen_contents.add(clean_content)

        logger.info(f"Reflection complete: Archived {archived_count} obsolete items, merged {merged_count} duplicates.")
        return {
            "archived_count": archived_count,
            "merged_count": merged_count,
            "reflection_timestamp": now
        }
