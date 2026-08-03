"""
Context Summarizer Module for Project Astra.
Uses token counting (tiktoken) to compress conversation logs into concise memory summaries.
"""

from typing import List, Optional
from app.models.memory_record import MemoryRecord, MemoryCategory, MemoryType
from app.utils.logger import logger


class ContextSummarizer:
    """
    Token-aware context compression and summarization service.
    """

    def __init__(self, max_token_threshold: int = 1000):
        self.max_token_threshold = max_token_threshold
        self._encoder = None

    def _get_encoder(self):
        if self._encoder is None:
            try:
                import tiktoken
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                logger.warning(f"Could not initialize tiktoken ({e}). Using word approximation.")
                self._encoder = None

    def count_tokens(self, text: str) -> int:
        """Counts exact or approximate tokens in text string."""
        self._get_encoder()
        if self._encoder:
            return len(self._encoder.encode(text))
        return len(text.split()) * 4 // 3  # Approximation fallback

    def should_summarize(self, records: List[MemoryRecord]) -> bool:
        """Checks if total token count across records exceeds threshold."""
        total_tokens = sum(self.count_tokens(r.content) for r in records)
        return total_tokens >= self.max_token_threshold

    def summarize_records(self, records: List[MemoryRecord]) -> MemoryRecord:
        """
        Compresses a sequence of memory records into a single summary record.
        """
        combined_text = "\n".join([r.content for r in records])
        logger.info(f"Summarizing {len(records)} memory records (~{self.count_tokens(combined_text)} tokens)...")

        # Extract main points for summary
        lines = [r.content for r in records if r.importance >= 4]
        if not lines:
            lines = [r.content for r in records]

        summary_content = f"Conversation Summary ({len(records)} turns): " + "; ".join(lines[:5])

        summary_record = MemoryRecord(
            content=summary_content,
            memory_type=MemoryType.EPISODIC,
            category=MemoryCategory.PERMANENT,
            importance=8,
            tags=["summary", "autocompressed"],
            metadata={"record_count": len(records), "original_tokens": self.count_tokens(combined_text)}
        )
        return summary_record
