"""
Memory Record Model for Project Astra.
Defines data structures for memory records, memory types, and categories.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
import time
import uuid


class MemoryType(str, Enum):
    WORKING = "working"     # Active in-RAM session history
    EPISODIC = "episodic"   # Experiential event & conversation history
    SEMANTIC = "semantic"   # Concepts, facts, knowledge, user preferences


class MemoryCategory(str, Enum):
    PERSONAL = "personal"
    PROJECTS = "projects"
    CODING = "coding"
    LEARNING = "learning"
    CAREER = "career"
    FINANCE = "finance"
    FAMILY = "family"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"


@dataclass
class MemoryRecord:
    """
    Represents a single atomic memory record in Astra's memory system.
    """
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    category: MemoryCategory = MemoryCategory.PERSONAL
    importance: int = 5  # Scale 1 (low) to 10 (critical)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    vector_embedding: Optional[List[float]] = None
    archived: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Converts memory record to JSON-serializable dictionary."""
        return {
            "record_id": self.record_id,
            "content": self.content,
            "memory_type": self.memory_type.value if isinstance(self.memory_type, MemoryType) else self.memory_type,
            "category": self.category.value if isinstance(self.category, MemoryCategory) else self.category,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "archived": self.archived
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """Constructs a MemoryRecord instance from dictionary data."""
        return cls(
            record_id=data.get("record_id", str(uuid.uuid4())),
            content=data.get("content", ""),
            memory_type=MemoryType(data.get("memory_type", "episodic")),
            category=MemoryCategory(data.get("category", "personal")),
            importance=data.get("importance", 5),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", time.time()),
            vector_embedding=data.get("vector_embedding"),
            archived=data.get("archived", False)
        )
