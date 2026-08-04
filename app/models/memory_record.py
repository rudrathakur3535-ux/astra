from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

class MemoryCategory(str, Enum):
    PERSONAL = "personal"
    PREFERENCE = "preference"
    FACT = "fact"
    SUMMARY = "summary"
    PERMANENT = "permanent"
    USER_PREFERENCE = "user_preference"
    SYSTEM_STATE = "system_state"
    CONVERSATION_FACT = "conversation_fact"
    CODE_CONTEXT = "code_context"
    GENERAL = "general"

class MemoryRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType
    content: str
    vector_embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: float = 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
