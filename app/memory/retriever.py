"""
Memory Retriever Module for Project Astra.
Combines recency (Working/Episodic) and relevance (Semantic Vector search) into unified context payloads.
"""

from typing import List, Dict, Any, Optional
from app.models.memory_record import MemoryRecord, MemoryCategory
from app.memory.working_memory import WorkingMemory
from app.memory.episodic_memory import EpisodicMemory
from app.memory.semantic_memory import SemanticMemory
from app.utils.logger import logger


class MemoryRetriever:
    """
    Hybrid context retrieval engine for injecting relevant long-term memory into LLM prompts.
    """

    def __init__(
        self,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory
    ):
        self.working_memory = working_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory

    def retrieve_context_for_prompt(
        self,
        user_query: str,
        top_semantic_k: int = 3,
        min_importance: int = 5
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive memory context dictionary before every LLM request.

        Returns:
            Dict containing:
                - 'working_context': List of active working memory turn strings
                - 'semantic_facts': List of relevant recall fact strings
                - 'recent_events': List of recent episodic memory event strings
                - 'formatted_context_block': Pre-formatted system prompt text block
        """
        # 1. Active Working Memory turns
        working_turns = self.working_memory.get_context_turns()

        # 2. Semantic Search based on current user query
        semantic_records = self.semantic_memory.recall_facts(
            query_text=user_query,
            top_k=top_semantic_k,
            min_importance=min_importance
        )

        # 3. Recent high-importance Episodic History
        recent_episodic = self.episodic_memory.get_recent_history(limit=5, min_importance=min_importance)

        # Assemble prompt memory block
        context_sections = []

        if semantic_records:
            facts_str = "\n".join([f"- {r.content} (Importance: {r.importance}/10)" for r in semantic_records])
            context_sections.append(f"### Relevant Memories & User Facts:\n{facts_str}")

        if recent_episodic:
            events_str = "\n".join([f"- {r.content}" for r in recent_episodic])
            context_sections.append(f"### Recent Activity & Events:\n{events_str}")

        formatted_block = "\n\n".join(context_sections)

        logger.debug(f"Retrieved {len(semantic_records)} semantic facts and {len(recent_episodic)} episodic events for query: '{user_query[:30]}...'")

        return {
            "working_turns": [r.content for r in working_turns],
            "semantic_facts": [r.content for r in semantic_records],
            "recent_events": [r.content for r in recent_episodic],
            "formatted_context_block": formatted_block
        }
