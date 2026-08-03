"""
Memory Query Model for Project Astra.
Defines query filtering parameter structures for hybrid memory retrieval.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from app.models.memory_record import MemoryType, MemoryCategory


@dataclass
class MemoryQuery:
    """
    Defines search parameters and constraints for querying memory adapters.
    """
    query_text: str = ""
    categories: Optional[List[MemoryCategory]] = None
    memory_types: Optional[List[MemoryType]] = None
    min_importance: int = 1
    top_k: int = 5
    include_archived: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None
